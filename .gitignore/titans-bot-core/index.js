require('dotenv').config();
const { Client, GatewayIntentBits, EmbedBuilder, AuditLogEvent, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
const { initializeApp } = require('firebase/app');
const { getFirestore, doc, onSnapshot } = require('firebase/firestore');

const client = new Client({ 
    intents: [
        GatewayIntentBits.Guilds, 
        GatewayIntentBits.GuildMessages, 
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildVoiceStates,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.GuildModeration
    ] 
});

const firebaseConfig = {
    apiKey: process.env.FIREBASE_API_KEY,
    projectId: process.env.FIREBASE_PROJECT_ID,
};
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const appId = 'titans-bot-prod';

const guildConfigs = new Map();
const activeReminders = new Map(); // Stocke les ID d'intervalles par guild

client.once('ready', () => {
    console.log(`🤖 Bot Titans prêt : ${client.user.tag}`);
    client.guilds.cache.forEach(guild => {
        onSnapshot(doc(db, 'artifacts', appId, 'public', 'data', 'guild_configs', guild.id), snap => {
            if(snap.exists()) {
                const config = snap.data();
                guildConfigs.set(guild.id, config);
                handleOperations(guild, config);
            } else {
                // Si la config disparait (ex: suppression de guild dans la db), on stop tout
                clearReminders(guild.id);
            }
        });
    });
});

function clearReminders(guildId) {
    if (activeReminders.has(guildId)) {
        activeReminders.get(guildId).forEach(itv => clearInterval(itv));
        activeReminders.delete(guildId);
    }
}

// --- LOGIQUE VOCALE (LOGS & TRIGGERS AVANCÉS) ---
client.on('voiceStateUpdate', async (oldState, newState) => {
    const config = guildConfigs.get(newState.guild.id);
    if (!config) return;

    const logChanId = config.voiceLogs?.channelId;
    const logChan = logChanId ? newState.guild.channels.cache.get(logChanId) : null;

    // 1. GESTION DES LOGS VOCAUX
    if (logChan) {
        const embed = new EmbedBuilder()
            .setAuthor({ name: newState.member.user.username, iconURL: newState.member.user.displayAvatarURL() })
            .setTimestamp()
            .setFooter({ text: 'Nexus Security • Titans Prime' });

        // JOIN
        if (!oldState.channelId && newState.channelId && config.voiceLogs.join) {
            embed.setColor('#2ecc71').setTitle('📥 ENTRÉE DÉTECTÉE').setDescription(`**Tenno :** <@${newState.member.id}>\n**Salon :** \`${newState.channel.name}\``);
            logChan.send({ embeds: [embed] });
        } 
        // LEAVE
        else if (oldState.channelId && !newState.channelId && config.voiceLogs.leave) {
            embed.setColor('#e74c3c').setTitle('📤 SORTIE DÉTECTÉE').setDescription(`**Tenno :** <@${oldState.member.id}>\n**Salon quitté :** \`${oldState.channel.name}\``);
            logChan.send({ embeds: [embed] });
        } 
        // MOVE
        else if (oldState.channelId && newState.channelId && oldState.channelId !== newState.channelId && config.voiceLogs.move) {
            let mover = null;
            try {
                const auditLogs = await newState.guild.fetchAuditLogs({ limit: 1, type: AuditLogEvent.MemberMove });
                const entry = auditLogs.entries.first();
                if (entry && entry.target.id === newState.id && (Date.now() - entry.createdTimestamp) < 5000) {
                    mover = entry.executor;
                }
            } catch (e) {}

            embed.setColor('#e67e22').setTitle('↔️ MOUVEMENT DÉTECTÉ');
            let desc = `**Tenno :** <@${newState.member.id}>\n**Ancien :** \`${oldState.channel.name}\`\n**Nouveau :** \`${newState.channel.name}\``;
            
            if (mover) {
                desc += `\n**Déplacé par :** <@${mover.id}>`;
            } else {
                desc += `\n**Note :** Le membre s'est déplacé de lui-même.`;
            }
            
            embed.setDescription(desc);
            logChan.send({ embeds: [embed] });
        }
    }

    // 2. GESTION DES TRIGGERS AVANCÉS
    if (newState.channelId && oldState.channelId !== newState.channelId) {
        const triggers = config.triggers || [];
        triggers.forEach(t => {
            if (t.voiceId === newState.channelId && t.channelId && t.message) {
                // Condition de rôle
                if (t.roleId && !newState.member.roles.cache.has(t.roleId)) return;

                const targetChan = newState.guild.channels.cache.get(t.channelId);
                if (targetChan) {
                    let finalMsg = t.message.replace('{user}', `<@${newState.member.id}>`).replace('{voice}', newState.channel.name);
                    targetChan.send(finalMsg).catch(() => {});
                }
            }
        });
    }
});

// --- TRIGGER OBTENTION DE RÔLE ---
client.on('guildMemberUpdate', async (oldMember, newMember) => {
    const config = guildConfigs.get(newMember.guild.id);
    if (!config || !config.roleGrantTriggers) return;

    const addedRoles = newMember.roles.cache.filter(role => !oldMember.roles.cache.has(role.id));
    if (addedRoles.size === 0) return;

    config.roleGrantTriggers.forEach(t => {
        if (addedRoles.has(t.roleId)) {
            const chan = newMember.guild.channels.cache.get(t.channelId);
            if (chan) {
                let msg = t.message.replace('{user}', `<@${newMember.id}>`).replace('{role}', addedRoles.get(t.roleId).name);
                chan.send(msg).catch(() => {});
            }
        }
    });
});

// --- GESTION DES INTERACTIONS (REACTION ROLES) ---
client.on('interactionCreate', async interaction => {
    if (!interaction.isButton()) return;
    if (!interaction.customId.startsWith('rr_')) return;

    const roleId = interaction.customId.replace('rr_', '');
    const role = interaction.guild.roles.cache.get(roleId);
    if (!role) return interaction.reply({ content: "Protocole introuvable (Rôle supprimé ?)", ephemeral: true });

    try {
        if (interaction.member.roles.cache.has(roleId)) {
            await interaction.member.roles.remove(roleId);
            await interaction.reply({ content: `✅ Rôle **${role.name}** retiré.`, ephemeral: true });
        } else {
            await interaction.member.roles.add(roleId);
            await interaction.reply({ content: `✅ Rôle **${role.name}** attribué.`, ephemeral: true });
        }
    } catch (e) {
        interaction.reply({ content: "⚠️ Liaison Nexus interrompue : Permissions insuffisantes pour gérer ce rôle.", ephemeral: true });
    }
});

// --- GESTION DES OPÉRATIONS (RAPPELS) ---
function handleOperations(guild, config) {
    const tirages = config.tirages || [];
    
    // On stop tout avant de relancer (permet de supprimer les triggers des events supprimés)
    clearReminders(guild.id);
    
    const intervals = [];

    tirages.forEach(op => {
        const targetId = op.triggerChanId || op.chanId;
        if (!targetId || !op.triggerInterval) return;

        const intervalMs = parseInt(op.triggerInterval) * 60 * 1000;
        if (intervalMs < 60000) return;

        const itv = setInterval(async () => {
            const chan = guild.channels.cache.get(targetId);
            if (!chan) return;

            let msg = op.triggerMessage || "⚠️ Rappel : Opération active !";
            msg = msg.replace('{title}', op.title);
            const ping = op.triggerRoleId ? `<@&${op.triggerRoleId}> ` : "";
            
            chan.send(`${ping}${msg}`).catch(() => {});
        }, intervalMs);

        intervals.push(itv);
    });

    activeReminders.set(guild.id, intervals);
}

// Anti-Lien
client.on('messageCreate', async (message) => {
    if (message.author.bot || !message.guild) return;
    const config = guildConfigs.get(message.guild.id);
    if (config?.security?.antiLink && /https?:\/\/[^\s]+/.test(message.content)) {
        await message.delete().catch(() => {});
        const m = await message.channel.send(`🚫 **${message.author.username}**, liens interdits.`);
        setTimeout(() => m.delete(), 3000);
    }
});

client.login(process.env.BOT_TOKEN);
