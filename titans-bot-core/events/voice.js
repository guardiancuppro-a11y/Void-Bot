const { Events, EmbedBuilder, AuditLogEvent } = require('discord.js');
const { getConfig } = require('../utils/firebase');

module.exports = {
    name: Events.VoiceStateUpdate,
    async execute(oldState, newState) {
        const config = getConfig(newState.guild.id);
        if (!config) return;
        const member = newState.member;
        if (!member || member.user.bot) return;

        const logs = config.voiceLogs || {};
        if (logs.channelId) {
            const chan = newState.guild.channels.cache.get(logs.channelId);
            if (chan) {
                const embed = new EmbedBuilder().setTimestamp();
                if (logs.showId) embed.setFooter({ text: `ID: ${member.id}` });
                if (logs.showAvatar) embed.setThumbnail(member.user.displayAvatarURL());

                let send = false;
                if (!oldState.channelId && newState.channelId && logs.join) {
                    embed.setColor('#57F287').setDescription(`📥 **${member.user.tag}** a rejoint **${newState.channel.toString()}**`);
                    send = true;
                } else if (oldState.channelId && !newState.channelId && logs.leave) {
                    embed.setColor('#ED4245').setDescription(`📤 **${member.user.tag}** a quitté **${oldState.channel.toString()}**`);
                    send = true;
                } else if (oldState.channelId && newState.channelId && oldState.channelId !== newState.channelId && logs.move) {
                    embed.setColor('#FEE75C');
                    let movedBy = "Lui-même";
                    if (logs.showResponsible) {
                        try {
                            const audit = await newState.guild.fetchAuditLogs({ limit: 1, type: AuditLogEvent.MemberMove });
                            const log = audit.entries.first();
                            if (log && log.target.id === member.id && (Date.now() - log.createdTimestamp) < 5000) movedBy = log.executor.tag;
                        } catch(e) {}
                    }
                    embed.setDescription(`↔️ **${member.user.tag}** déplacé\nDe: ${oldState.channel.toString()}\nÀ: ${newState.channel.toString()}\nPar: ${movedBy}`);
                    send = true;
                }
                if (send) chan.send({ embeds: [embed] }).catch(()=>{});
            }
        }
    }
};
