const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const { getConfig } = require('../../firebase');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('event')
        .setDescription('Gérer les événements')
        .addSubcommand(sub => 
            sub.setName('publish')
            .setDescription('Publier un événement configuré sur le dashboard')
            .addStringOption(opt => opt.setName('id').setDescription('L\'ID de l\'event (voir dashboard)').setRequired(true))
        ),
    async execute(interaction) {
        const sub = interaction.options.getSubcommand();
        const guild = interaction.guild;
        const config = getConfig(guild.id);

        if (sub === 'publish') {
            const eventId = interaction.options.getString('id');
            const events = config.events || [];
            
            // On cherche l'event par ID (ou par titre approximatif si ID numérique)
            const event = events.find(e => String(e.id) === eventId || e.title === eventId);

            if (!event) {
                return interaction.reply({ content: '❌ Événement introuvable. Vérifiez le Dashboard.', ephemeral: true });
            }

            const embed = new EmbedBuilder()
                .setTitle(`📅 ${event.title}`)
                .setDescription(event.desc)
                .addFields(
                    { name: 'Date', value: event.date ? `<t:${Math.floor(new Date(event.date).getTime()/1000)}:F>` : 'Non définie' }
                )
                .setColor(config.theme?.color || '#5865F2')
                .setFooter({ text: config.theme?.footer || 'Titans Events' });

            if (event.isGiveaway) {
                embed.addFields({ name: '🎁 Giveaway', value: 'Réagissez avec 🎉 pour participer !' });
            }

            await interaction.reply({ embeds: [embed] });
            const msg = await interaction.fetchReply();
            
            if (event.isGiveaway) {
                msg.react('🎉');
            }
        }
    },
};
