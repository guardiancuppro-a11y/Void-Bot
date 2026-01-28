require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const app = express();
const PORT = 3001;

app.use(cors({ origin: 'http://localhost:5173', credentials: true }));
app.use(express.json());
app.use(cookieParser());

const DISCORD_API = 'https://discord.com/api/v10';
const CLIENT_ID = process.env.DISCORD_CLIENT_ID;
const CLIENT_SECRET = process.env.DISCORD_CLIENT_SECRET;
const REDIRECT_URI = 'http://localhost:3001/api/auth/callback';
const BOT_TOKEN = process.env.BOT_TOKEN;

// --- AUTHENTIFICATION ---
app.get('/api/auth/login', (req, res) => {
    const url = `https://discord.com/oauth2/authorize?client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&response_type=code&scope=identify%20guilds`;
    res.redirect(url);
});

app.get('/api/auth/callback', async (req, res) => {
    const { code } = req.query;
    try {
        const resp = await axios.post(`${DISCORD_API}/oauth2/token`, new URLSearchParams({
            client_id: CLIENT_ID, client_secret: CLIENT_SECRET,
            grant_type: 'authorization_code', code, redirect_uri: REDIRECT_URI
        }), { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
        res.cookie('access_token', resp.data.access_token, { httpOnly: true });
        res.redirect('http://localhost:5173');
    } catch (e) { res.redirect('http://localhost:5173?error=auth'); }
});

app.get('/api/user/guilds', async (req, res) => {
    const token = req.cookies.access_token;
    if (!token) return res.status(401).json({ error: 'No token' });
    try {
        const user = await axios.get(`${DISCORD_API}/users/@me`, { headers: { Authorization: `Bearer ${token}` } });
        const guilds = await axios.get(`${DISCORD_API}/users/@me/guilds`, { headers: { Authorization: `Bearer ${token}` } });
        const adminGuilds = guilds.data.filter(g => (BigInt(g.permissions) & 0x8n) === 0x8n);
        res.json({ user: user.data, guilds: adminGuilds.map(g => ({ ...g, botPresent: true })) });
    } catch { res.status(500).json({ error: 'Fail' }); }
});

// --- ACTIONS BOT (REACTION ROLES) ---
app.post('/api/bot/reaction-role', async (req, res) => {
    try {
        const { channelId, title, desc, color, mappings } = req.body;
        const colorHex = parseInt(color.replace('#',''), 16);
        
        // Boutons Discord
        const components = [{
            type: 1,
            components: mappings.slice(0, 5).map(m => ({
                type: 2,
                style: 2, // Secondary (Gray)
                label: m.label || "Rôle",
                custom_id: `rr_${m.roleId}`,
            }))
        }];

        await axios.post(`${DISCORD_API}/channels/${channelId}/messages`, {
            embeds: [{ title, description: desc, color: colorHex }],
            components
        }, { headers: { Authorization: `Bot ${BOT_TOKEN}` } });
        
        res.json({ ok: true });
    } catch (e) { res.status(500).json({ error: e.message }); }
});

// --- ACTIONS BOT (EMBEDS & OPERATIONS) ---
app.post('/api/bot/embed/:guildId', async (req, res) => {
    try {
        const { chanId, embed } = req.body;
        const color = parseInt(embed.color.replace('#',''), 16);
        await axios.post(`${DISCORD_API}/channels/${chanId}/messages`, {
            embeds: [{ 
                title: embed.title, 
                description: embed.desc, 
                color,
                footer: { text: embed.footer },
                thumbnail: embed.thumb ? { url: embed.thumb } : null,
                image: embed.img ? { url: embed.img } : null
            }]
        }, { headers: { Authorization: `Bot ${BOT_TOKEN}` } });
        res.json({ ok: true });
    } catch (e) { res.status(500).json({ error: e.message }); }
});

app.post('/api/bot/operation/:guildId', async (req, res) => {
    try {
        const ev = req.body;
        const color = parseInt(ev.color.replace('#',''), 16);
        await axios.post(`${DISCORD_API}/channels/${ev.chanId}/messages`, {
            embeds: [{ 
                title: ev.title, 
                description: ev.desc, 
                color,
                fields: [
                    { name: 'Lots', value: ev.prize, inline: true },
                    { name: 'Expiration', value: `${ev.timer}h`, inline: true }
                ],
                footer: { text: ev.footer },
                thumbnail: ev.thumbnail ? { url: ev.thumbnail } : null,
                image: ev.img ? { url: ev.img } : null
            }]
        }, { headers: { Authorization: `Bot ${BOT_TOKEN}` } });
        res.json({ ok: true });
    } catch (e) { res.status(500).json({ error: e.message }); }
});

// --- MODÉRATION ---
app.post('/api/mod/:type/:guildId', async (req, res) => {
    const { userId, reason } = req.body;
    const { type, guildId } = req.params;
    try {
        if (type === 'ban') {
            await axios.put(`${DISCORD_API}/guilds/${guildId}/bans/${userId}`, { reason }, { headers: { Authorization: `Bot ${BOT_TOKEN}` } });
        } else if (type === 'kick') {
            await axios.delete(`${DISCORD_API}/guilds/${guildId}/members/${userId}`, { headers: { Authorization: `Bot ${BOT_TOKEN}` } });
        }
        res.json({ ok: true });
    } catch (e) { res.status(500).json({ error: e.message }); }
});

// --- HELPERS ---
app.get('/api/guilds/:id/channels', async (req, res) => {
    try {
        const r = await axios.get(`${DISCORD_API}/guilds/${req.params.id}/channels`, { headers: { Authorization: `Bot ${BOT_TOKEN}` } });
        res.json(r.data.filter(c => [0, 2, 4].includes(c.type)).map(c => ({ id: c.id, name: c.name, type: c.type === 2 ? 'voice' : 'text' })));
    } catch { res.json([]); }
});

app.get('/api/guilds/:id/roles', async (req, res) => {
    try {
        const r = await axios.get(`${DISCORD_API}/guilds/${req.params.id}/roles`, { headers: { Authorization: `Bot ${BOT_TOKEN}` } });
        res.json(r.data.filter(r => r.name !== '@everyone').map(r => ({ id: r.id, name: r.name })));
    } catch { res.json([]); }
});

app.get('/api/guilds/:id/members', async (req, res) => {
    try {
        const r = await axios.get(`${DISCORD_API}/guilds/${req.params.id}/members?limit=100`, { headers: { Authorization: `Bot ${BOT_TOKEN}` } });
        res.json(r.data.map(m => ({ id: m.user.id, tag: m.user.username })));
    } catch { res.json([]); }
});

app.listen(PORT, () => console.log(`API running on ${PORT}`));
