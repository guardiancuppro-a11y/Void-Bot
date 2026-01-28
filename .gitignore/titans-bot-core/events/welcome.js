const { Events } = require('discord.js');
const { getConfig } = require('../utils/firebase');

module.exports = {
    name: Events.GuildMemberAdd,
    async execute(member) {
        const config = getConfig(member.guild.id);
        if (!config) return;

        // Auto-Role
        if (config.autoRole && config.autoRole.roleId) {
            const role = member.guild.roles.cache.get(config.autoRole.roleId);
            if (role) setTimeout(() => member.roles.add(role).catch(() => {}), 1500);
        }

        // Message Bienvenue
        if (config.welcome && config.welcome.channelId) {
            const channel = member.guild.channels.cache.get(config.welcome.channelId);
            if (channel) {
                let content = config.welcome.message || "Bienvenue {user} !";
                content = content.replace('{user}', member.toString())
                                 .replace('{username}', member.user.username)
                                 .replace('{server}', member.guild.name)
                                 .replace('{memberCount}', member.guild.memberCount);
                channel.send(content).catch(() => {});
            }
        }
    },
};
