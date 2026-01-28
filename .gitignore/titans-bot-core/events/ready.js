const { Events, ActivityType } = require('discord.js');
const { watchConfig } = require('../utils/firebase');

module.exports = {
    name: Events.ClientReady,
    once: true,
    execute(client) {
        console.log(`✅ Bot Opérationnel: ${client.user.tag}`);
        client.user.setActivity('Titans IA', { type: ActivityType.Watching });
        client.guilds.cache.forEach(g => watchConfig(g.id));
    },
};
