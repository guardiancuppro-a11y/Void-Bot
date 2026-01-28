import os

project_name = "titans-ecosystem"

# ==========================================
# 1. LE BOT DISCORD (Celui qui exécute les actions)
# ==========================================

bot_package_json = """{
  "name": "titans-bot",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "dev": "nodemon index.js",
    "start": "node index.js"
  },
  "dependencies": {
    "discord.js": "^14.14.1",
    "dotenv": "^16.3.1",
    "firebase": "^10.7.1"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}"""

bot_index_js = """require('dotenv').config();
const { Client, GatewayIntentBits, EmbedBuilder, AuditLogEvent, ActivityType } = require('discord.js');
const { initializeApp } = require('firebase/app');
const { getFirestore, doc, onSnapshot } = require('firebase/firestore');

// --- FIREBASE SETUP ---
const firebaseConfig = {
  apiKey: process.env.FIREBASE_API_KEY,
  authDomain: process.env.FIREBASE_PROJECT_ID + ".firebaseapp.com",
  projectId: process.env.FIREBASE_PROJECT_ID,
  storageBucket: process.env.FIREBASE_PROJECT_ID + ".appspot.com",
  messagingSenderId: process.env.FIREBASE_SENDER_ID,
  appId: process.env.FIREBASE_APP_ID
};
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const appId = 'titans-bot-prod';

// Cache des configs (GuildID -> Config)
const guildConfigs = new Map();

// Fonction pour surveiller la config d'un serveur
function watchConfig(guildId) {
    if (guildConfigs.has(guildId)) return;
    console.log(`[Config] Ecoute active pour ${guildId}`);
    onSnapshot(doc(db, 'artifacts', appId, 'public', 'data', `config_${guildId}`), (snap) => {
        if (snap.exists()) guildConfigs.set(guildId, snap.data());
    });
}

// --- BOT SETUP ---
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.GuildVoiceStates,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.GuildPresences,
        GatewayIntentBits.GuildBans
    ]
});

client.once('ready', () => {
    console.log(`🤖 ${client.user.tag} est en ligne !`);
    client.user.setActivity('le Dashboard', { type: ActivityType.Watching });
    client.guilds.cache.forEach(g => watchConfig(g.id));
});

client.on('guildCreate', g => watchConfig(g.id));

// ==========================================
// 1. MODULE LOGS VOCAUX & TRIGGERS
// ==========================================
client.on('voiceStateUpdate', async (oldState, newState) => {
    const guild = newState.guild;
    const config = guildConfigs.get(guild.id);
    if (!config) return;

    const member = newState.member;
    if (member.user.bot) return;

    // --- LOGS ---
    const logs = config.voiceLogs || {};
    if (logs.channelId) {
        const channel = guild.channels.cache.get(logs.channelId);
        if (channel && channel.isTextBased()) {
            let embed = new EmbedBuilder().setTimestamp().setFooter({ text: 'Titans Voice Logs' });
            
            // Join
            if (!oldState.channelId && newState.channelId && logs.join) {
                embed.setColor('#57F287').setDescription(`📥 **${member.user.tag}** a rejoint **${newState.channel.name}**`);
                channel.send({ embeds: [embed] }).catch(() => {});
            }
            // Leave
            else if (oldState.channelId && !newState.channelId && logs.leave) {
                embed.setColor('#ED4245').setDescription(`📤 **${member.user.tag}** a quitté **${oldState.channel.name}**`);
                channel.send({ embeds: [embed] }).catch(() => {});
            }
            // Move
            else if (oldState.channelId && newState.channelId && oldState.channelId !== newState.channelId && logs.move) {
                embed.setColor('#FEE75C').setDescription(`↔️ **${member.user.tag}** a bougé\nDe : **${oldState.channel.name}**\nVers : **${newState.channel.name}**`);
                channel.send({ embeds: [embed] }).catch(() => {});
            }
        }
    }

    // --- TRIGGERS ---
    // Si quelqu'un rejoint un salon spécifique
    if (newState.channelId && (oldState.channelId !== newState.channelId)) {
        const triggers = config.triggers || [];
        triggers.forEach(async (t) => {
            if (t.voiceId === newState.channelId) {
                // Vérif Role
                if (t.roleId && !member.roles.cache.has(t.roleId)) return;
                
                const targetChan = guild.channels.cache.get(t.channelId);
                if (targetChan) {
                    let msg = t.message
                        .replace('{user}', member.toString())
                        .replace('{voice}', newState.channel.toString());
                    
                    if (t.ghostPing) {
                        const m = await targetChan.send(member.toString());
                        await m.delete();
                    }
                    targetChan.send(msg).catch(() => {});
                }
            }
        });
    }
});

// ==========================================
// 2. MODULE BIENVENUE & AUTO-ROLE
// ==========================================
client.on('guildMemberAdd', async (member) => {
    const config = guildConfigs.get(member.guild.id);
    if (!config) return;

    // Auto-Role
    if (config.autoRole && config.autoRole.roleId) {
        const role = member.guild.roles.cache.get(config.autoRole.roleId);
        if (role) member.roles.add(role).catch(console.error);
    }

    // Welcome Message
    if (config.welcome && config.welcome.channelId) {
        const channel = member.guild.channels.cache.get(config.welcome.channelId);
        if (channel) {
            let content = config.welcome.message || "Bienvenue {user} !";
            content = content.replace('{user}', member.toString()).replace('{server}', member.guild.name);
            channel.send(content).catch(() => {});
        }
    }
});

// ==========================================
// 3. MODULE MODERATION (BAN/KICK)
// ==========================================
client.on('guildBanAdd', async (ban) => {
    const config = guildConfigs.get(ban.guild.id);
    if (!config || !config.modLogs || !config.modLogs.channelId || !config.modLogs.ban) return;

    const channel = ban.guild.channels.cache.get(config.modLogs.channelId);
    if (channel) {
        // Tentative récupération auteur via Audit Log
        let executor = "Inconnu";
        try {
            const audits = await ban.guild.fetchAuditLogs({ type: AuditLogEvent.MemberBanAdd, limit: 1 });
            const entry = audits.entries.first();
            if (entry && entry.target.id === ban.user.id) executor = entry.executor.tag;
        } catch(e) {}

        const embed = new EmbedBuilder()
            .setTitle('🔨 Membre Banni')
            .setColor('#000000')
            .addFields(
                { name: 'Utilisateur', value: ban.user.tag, inline: true },
                { name: 'Par', value: executor, inline: true }
            )
            .setTimestamp();
        channel.send({ embeds: [embed] }).catch(() => {});
    }
});

client.login(process.env.DISCORD_TOKEN);
"""

bot_env = """DISCORD_TOKEN=METTRE_TON_TOKEN_BOT_ICI
# Copie ici les infos FIREBASE (les mêmes que pour le client)
FIREBASE_API_KEY=...
FIREBASE_PROJECT_ID=...
FIREBASE_SENDER_ID=...
FIREBASE_APP_ID=...
"""

# ==========================================
# 2. LE BACKEND (API OAuth2 & Proxy)
# ==========================================
# (Similaire à avant, essentiel pour la connexion)

server_package_json = """{
  "name": "titans-server",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": { "dev": "nodemon index.js" },
  "dependencies": { "axios": "^1.6.0", "cookie-parser": "^1.4.6", "cors": "^2.8.5", "dotenv": "^16.3.1", "express": "^4.18.2" },
  "devDependencies": { "nodemon": "^3.0.1" }
}"""

server_index_js = """require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const app = express();
const PORT = 3001;

app.use(cors({ origin: 'http://localhost:5173', credentials: true }));
app.use(cookieParser());
app.use(express.json());

const DISCORD_API = 'https://discord.com/api/v10';

// Auth Middleware
const requireAuth = (req, res, next) => {
    if(!req.cookies.access_token) return res.status(401).json({error: 'No token'});
    req.token = req.cookies.access_token;
    next();
};

// OAuth
app.get('/api/auth/login', (req, res) => {
    res.redirect(`https://discord.com/oauth2/authorize?client_id=${process.env.CLIENT_ID}&redirect_uri=${encodeURIComponent(process.env.REDIRECT_URI)}&response_type=code&scope=identify%20guilds`);
});

app.get('/api/auth/callback', async (req, res) => {
    try {
        const resp = await axios.post(`${DISCORD_API}/oauth2/token`, new URLSearchParams({
            client_id: process.env.CLIENT_ID, client_secret: process.env.CLIENT_SECRET,
            grant_type: 'authorization_code', code: req.query.code, redirect_uri: process.env.REDIRECT_URI
        }));
        res.cookie('access_token', resp.data.access_token, {httpOnly: true});
        res.redirect('http://localhost:5173');
    } catch(e) { res.redirect('http://localhost:5173/?error=true'); }
});

app.post('/api/auth/logout', (req, res) => { res.clearCookie('access_token'); res.json({ok:true}); });

// Data
app.get('/api/user/guilds', requireAuth, async (req, res) => {
    try {
        const user = await axios.get(`${DISCORD_API}/users/@me`, {headers:{Authorization:`Bearer ${req.token}`}});
        const guilds = await axios.get(`${DISCORD_API}/users/@me/guilds`, {headers:{Authorization:`Bearer ${req.token}`}});
        const adminGuilds = guilds.data.filter(g => (BigInt(g.permissions) & 0x8n) === 0x8n);
        
        // Check Bot Presence
        const result = await Promise.all(adminGuilds.map(async g => {
            try { await axios.get(`${DISCORD_API}/guilds/${g.id}`, {headers:{Authorization:`Bot ${process.env.BOT_TOKEN}`}}); return {...g, botPresent:true}; }
            catch { return {...g, botPresent:false}; }
        }));
        res.json({user:user.data, guilds:result});
    } catch { res.sendStatus(500); }
});

app.get('/api/guilds/:id/channels', requireAuth, async (req, res) => {
    try {
        const ch = await axios.get(`${DISCORD_API}/guilds/${req.params.id}/channels`, {headers:{Authorization:`Bot ${process.env.BOT_TOKEN}`}});
        res.json(ch.data.filter(c => [0,2].includes(c.type)).map(c => ({id:c.id, name:c.name, type:c.type===2?'voice':'text'})));
    } catch { res.json([]); }
});

// Embed Sender (Direct Action)
app.post('/api/bot/embed/:guildId', requireAuth, async (req, res) => {
    try {
        const { channelId, embed } = req.body;
        // Basic sanitization
        const clean = { 
            title: embed.title, description: embed.description, 
            color: parseInt(embed.color.replace('#',''), 16),
            fields: embed.fields || []
        };
        if(embed.image?.url) clean.image = {url: embed.image.url};
        if(embed.thumbnail?.url) clean.thumbnail = {url: embed.thumbnail.url};
        
        await axios.post(`${DISCORD_API}/channels/${channelId}/messages`, {embeds:[clean]}, {headers:{Authorization:`Bot ${process.env.BOT_TOKEN}`}});
        res.json({ok:true});
    } catch(e) { console.error(e.response?.data); res.status(500).json({error: e.message}); }
});

app.listen(3001, () => console.log('API running on 3001'));
"""

server_env = """CLIENT_ID=...
CLIENT_SECRET=...
BOT_TOKEN=...
REDIRECT_URI=http://localhost:3001/api/auth/callback"""

# ==========================================
# 3. LE FRONTEND (React Dashboard)
# ==========================================

client_package_json = """{
  "name": "titans-client",
  "version": "2.1.0",
  "type": "module",
  "scripts": { "dev": "vite" },
  "dependencies": { "lucide-react": "^0.292.0", "react": "^18.2.0", "react-dom": "^18.2.0", "firebase": "^10.6.0" },
  "devDependencies": { "@vitejs/plugin-react": "^4.2.0", "autoprefixer": "^10.4.16", "postcss": "^8.4.31", "tailwindcss": "^3.3.5", "vite": "^5.0.0" }
}"""

client_vite_config = """import { defineConfig } from 'vite'; import react from '@vitejs/plugin-react';
export default defineConfig({ plugins: [react()], server: { port: 5173, proxy: { '/api': 'http://localhost:3001' } } });"""

client_app_jsx = """import React, { useState, useEffect } from 'react';
import { LayoutDashboard, Mic, Zap, ShieldAlert, MessageSquare, LogOut, Menu, UserPlus, Gift, Save, ArrowLeft, Send, Plus, Trash2 } from 'lucide-react';
import { initializeApp } from 'firebase/app';
import { getFirestore, doc, getDoc, setDoc } from 'firebase/firestore';

// --- CONFIG ---
// REMPLACE CECI :
const firebaseConfig = {
    apiKey: "API_KEY",
    authDomain: "PROJECT_ID.firebaseapp.com",
    projectId: "PROJECT_ID",
    storageBucket: "PROJECT_ID.appspot.com",
    messagingSenderId: "SENDER_ID",
    appId: "APP_ID"
};
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const appId = 'titans-bot-prod';

// --- COMPONENTS ---
const Card = ({children}) => <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden p-6 space-y-4">{children}</div>;
const Button = ({children, onClick, variant='primary', className=''}) => {
    const vars = { primary: 'bg-indigo-600 hover:bg-indigo-500', secondary: 'bg-zinc-800 hover:bg-zinc-700', danger: 'bg-red-900/50 text-red-400' };
    return <button onClick={onClick} className={`px-4 py-2 rounded-lg font-medium text-white transition-colors flex items-center justify-center gap-2 ${vars[variant]||vars.primary} ${className}`}>{children}</button>;
};
const Input = ({label, value, onChange, placeholder, type='text'}) => (
    <div className="space-y-1"><label className="text-sm text-zinc-400">{label}</label>
    <input type={type} value={value} onChange={onChange} placeholder={placeholder} className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white focus:ring-2 ring-indigo-500 outline-none"/></div>
);
const Select = ({label, value, onChange, options}) => (
    <div className="space-y-1"><label className="text-sm text-zinc-400">{label}</label>
    <select value={value} onChange={onChange} className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white outline-none">
        <option value="">Sélectionner...</option>{options.map(o=><option key={o.id} value={o.id}>{o.name}</option>)}
    </select></div>
);
const Toggle = ({label, checked, onChange}) => (
    <div className="flex justify-between items-center p-3 bg-zinc-950 rounded-lg border border-zinc-800">
        <span className="text-sm text-zinc-300">{label}</span>
        <button onClick={()=>onChange(!checked)} className={`w-10 h-6 rounded-full relative transition-colors ${checked?'bg-indigo-600':'bg-zinc-700'}`}>
            <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${checked?'translate-x-4':''}`}/>
        </button>
    </div>
);

// --- MODULES ---
const WelcomeModule = ({config, update, channels, roles}) => { // Ajout roles si dispo, sinon champ texte ID
    const c = config.welcome || {};
    const ar = config.autoRole || {};
    return (
        <div className="space-y-6">
            <Card>
                <h3 className="text-xl font-bold text-white flex gap-2"><UserPlus/> Bienvenue</h3>
                <Select label="Salon de Bienvenue" options={channels.filter(x=>x.type==='text')} value={c.channelId||''} onChange={e=>update('welcome', {...c, channelId:e.target.value})} />
                <Input label="Message ({user}, {server})" value={c.message||''} onChange={e=>update('welcome', {...c, message:e.target.value})} placeholder="Bienvenue {user} !" />
            </Card>
            <Card>
                <h3 className="text-xl font-bold text-white">Auto-Rôle</h3>
                <Input label="ID du Rôle à donner" value={ar.roleId||''} onChange={e=>update('autoRole', {...ar, roleId:e.target.value})} placeholder="Ex: 987654321..." />
            </Card>
        </div>
    );
};

const VoiceLogsModule = ({config, update, channels}) => {
    const l = config.voiceLogs || {};
    const set = (k,v) => update('voiceLogs', {...l, [k]:v});
    return (
        <Card>
            <h3 className="text-xl font-bold text-white flex gap-2"><Mic/> Logs Vocaux</h3>
            <Select label="Salon de Logs" options={channels.filter(x=>x.type==='text')} value={l.channelId||''} onChange={e=>set('channelId', e.target.value)} />
            <div className="grid grid-cols-2 gap-4 mt-4">
                <Toggle label="Join" checked={l.join} onChange={v=>set('join',v)} />
                <Toggle label="Leave" checked={l.leave} onChange={v=>set('leave',v)} />
                <Toggle label="Move" checked={l.move} onChange={v=>set('move',v)} />
            </div>
        </Card>
    );
};

const EmbedBuilder = ({guild, channels}) => {
    const [e, setE] = useState({title:'Titre', description:'Desc', color:'#5865F2', fields:[]});
    const [chan, setChan] = useState('');
    
    const send = async () => {
        if(!chan) return alert('Salon ?');
        await fetch(`/api/bot/embed/${guild.id}`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({channelId:chan, embed:e})});
        alert('Envoyé !');
    };

    return (
        <div className="grid grid-cols-2 gap-6">
            <div className="space-y-6">
                <Card>
                    <h3 className="font-bold text-white mb-4">Créateur</h3>
                    <Select label="Salon" options={channels.filter(c=>c.type==='text')} value={chan} onChange={ev=>setChan(ev.target.value)} />
                    <Input label="Titre" value={e.title} onChange={ev=>setE({...e, title:ev.target.value})} />
                    <Input label="Description" value={e.description} onChange={ev=>setE({...e, description:ev.target.value})} />
                    <Input label="Couleur" type="color" value={e.color} onChange={ev=>setE({...e, color:ev.target.value})} />
                    <div className="pt-2"><Button onClick={send} variant="primary" className="w-full"><Send size={16}/> Envoyer</Button></div>
                </Card>
            </div>
            <div className="space-y-6">
                <div className="text-xs font-bold text-zinc-500 uppercase">Aperçu</div>
                <div className="bg-[#313338] p-4 rounded border border-zinc-800 flex gap-3">
                    <div className="w-10 h-10 rounded-full bg-indigo-500 flex items-center justify-center font-bold text-white">B</div>
                    <div className="flex-1">
                        <div className="flex items-baseline gap-2"><span className="text-white font-bold">Bot</span><span className="bg-[#5865F2] text-xs px-1 rounded text-white">BOT</span></div>
                        <div className="mt-1 border-l-4 bg-[#2b2d31] p-3 rounded-r" style={{borderLeftColor:e.color}}>
                            <div className="font-bold text-white">{e.title}</div>
                            <div className="text-zinc-300 text-sm">{e.description}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

// --- MAIN APP ---
export default function App() {
    const [user, setUser] = useState(null);
    const [guilds, setGuilds] = useState([]);
    const [currentGuild, setCurrentGuild] = useState(null);
    const [channels, setChannels] = useState([]);
    const [config, setConfig] = useState({});
    const [module, setModule] = useState('home');

    useEffect(() => {
        fetch('/api/user/guilds').then(r=>r.json()).then(d=>{ setUser(d.user); setGuilds(d.guilds); }).catch(console.error);
    }, []);

    const selectGuild = async (g) => {
        if(!g.botPresent) return alert("Le bot n'est pas sur ce serveur !");
        setCurrentGuild(g);
        // Load Channels
        fetch(`/api/guilds/${g.id}/channels`).then(r=>r.json()).then(setChannels);
        // Load Config
        const snap = await getDoc(doc(db, 'artifacts', appId, 'public', 'data', `config_${g.id}`));
        if(snap.exists()) setConfig(snap.data()); else setConfig({});
    };

    const updateConfig = async (key, val) => {
        const n = {...config, [key]:val};
        setConfig(n);
        await setDoc(doc(db, 'artifacts', appId, 'public', 'data', `config_${currentGuild.id}`), n, {merge:true});
    };

    if(!user) return <div className="min-h-screen bg-black flex items-center justify-center"><Button asLink={true} onClick={()=>window.location.href='/api/auth/login'}>Connexion Discord</Button></div>;

    if(!currentGuild) return (
        <div className="min-h-screen bg-black p-10 flex flex-col items-center">
            <h1 className="text-3xl text-white font-bold mb-8">Sélectionner un serveur</h1>
            <div className="grid grid-cols-3 gap-4">
                {guilds.map(g => (
                    <button key={g.id} onClick={()=>selectGuild(g)} className={`p-6 rounded-xl border border-zinc-800 flex flex-col items-center gap-3 hover:bg-zinc-900 ${!g.botPresent && 'opacity-50'}`}>
                        <div className="w-16 h-16 bg-zinc-800 rounded-full flex items-center justify-center text-white font-bold">{g.name.substring(0,2)}</div>
                        <div className="text-white font-bold">{g.name}</div>
                        {!g.botPresent && <span className="text-xs text-red-400">Bot Manquant</span>}
                    </button>
                ))}
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-black flex text-white font-sans">
            <aside className="w-64 border-r border-zinc-800 p-4 flex flex-col gap-1">
                <div className="mb-6 px-2 font-bold text-xl bg-gradient-to-r from-indigo-500 to-purple-500 bg-clip-text text-transparent">TITANS</div>
                <Button variant="secondary" onClick={()=>setCurrentGuild(null)} className="mb-4 text-xs"><ArrowLeft size={14}/> Changer Serveur</Button>
                <button onClick={()=>setModule('home')} className={`text-left px-3 py-2 rounded ${module==='home'?'bg-indigo-900/30 text-indigo-400':'text-zinc-400 hover:text-white'}`}>Accueil</button>
                <button onClick={()=>setModule('welcome')} className={`text-left px-3 py-2 rounded ${module==='welcome'?'bg-indigo-900/30 text-indigo-400':'text-zinc-400 hover:text-white'}`}>Bienvenue</button>
                <button onClick={()=>setModule('voice')} className={`text-left px-3 py-2 rounded ${module==='voice'?'bg-indigo-900/30 text-indigo-400':'text-zinc-400 hover:text-white'}`}>Logs Vocaux</button>
                <button onClick={()=>setModule('embed')} className={`text-left px-3 py-2 rounded ${module==='embed'?'bg-indigo-900/30 text-indigo-400':'text-zinc-400 hover:text-white'}`}>Embed Builder</button>
            </aside>
            <main className="flex-1 p-8 overflow-y-auto">
                {module==='home' && <h1 className="text-3xl font-bold">Configuration de {currentGuild.name}</h1>}
                {module==='welcome' && <WelcomeModule config={config} update={updateConfig} channels={channels} />}
                {module==='voice' && <VoiceLogsModule config={config} update={updateConfig} channels={channels} />}
                {module==='embed' && <EmbedBuilder guild={currentGuild} channels={channels} />}
            </main>
        </div>
    );
}
"""

# --- SCRIPT GENERATION ---
def create_file(path, content):
    full_path = os.path.join(project_name, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    if "env" in path and os.path.exists(full_path): return
    with open(full_path, "w", encoding="utf-8") as f: f.write(content)
    print(f"File created: {path}")

# Structure folders
for d in ["bot", "server", "client/src"]:
    os.makedirs(os.path.join(project_name, d), exist_ok=True)

# Bot Files
create_file("bot/package.json", bot_package_json)
create_file("bot/index.js", bot_index_js)
create_file("bot/.env", bot_env)

# Server Files
create_file("server/package.json", server_package_json)
create_file("server/index.js", server_index_js)
create_file("server/.env", server_env)

# Client Files
create_file("client/package.json", client_package_json)
create_file("client/vite.config.js", client_vite_config)
create_file("client/src/App.jsx", client_app_jsx)

# Static client files
create_file("client/index.html", """<!doctype html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>Dashboard</title></head><body><div id="root"></div><script type="module" src="/src/main.jsx"></script></body></html>""")
create_file("client/tailwind.config.js", """export default { content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"], theme: { extend: {} }, plugins: [] }""")
create_file("client/postcss.config.js", """export default { plugins: { tailwindcss: {}, autoprefixer: {} } }""")
create_file("client/src/index.css", """@tailwind base; @tailwind components; @tailwind utilities; body { background-color: black; color: white; }""")
create_file("client/src/main.jsx", """import React from 'react'; import ReactDOM from 'react-dom/client'; import App from './App.jsx'; import './index.css'; ReactDOM.createRoot(document.getElementById('root')).render(<App />);""")

print("\n✅ ECOSYSTÈME GÉNÉRÉ ! Trois terminaux nécessaires :")
print("1. cd bot && npm install && npm run dev")
print("2. cd server && npm install && npm run dev")
print("3. cd client && npm install && npm run dev")