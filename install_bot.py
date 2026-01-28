import os

# Configuration des dossiers
dashboard_dir = "titans-dashboard"
bot_dir = "titans-bot-core"
ai_dir = "titans-ai-service"

# ==========================================
# 0. NETTOYAGE & PRÉPARATION
# ==========================================
files_to_remove = [
    f"{bot_dir}/events/voiceStateUpdate.js", 
    f"{bot_dir}/firebase.js",
    f"{bot_dir}/events/interactionCreate.js"
]
print("🧹 Nettoyage des anciens fichiers...")
for f in files_to_remove:
    if os.path.exists(f):
        try: os.remove(f)
        except: pass

# ==========================================
# 1. RÉCUPÉRATION DES CLÉS (.env)
# ==========================================
env_vars = {}
if os.path.exists(f"{bot_dir}/.env"):
    with open(f"{bot_dir}/.env", "r", encoding="utf-8") as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                env_vars[key] = val.replace('"', '').replace("'", "")

fb_api_key = env_vars.get("FIREBASE_API_KEY", "TON_API_KEY")
fb_project_id = env_vars.get("FIREBASE_PROJECT_ID", "TON_PROJECT_ID")
fb_sender_id = env_vars.get("FIREBASE_SENDER_ID", "TON_SENDER_ID")
fb_app_id = env_vars.get("FIREBASE_APP_ID", "TON_APP_ID")

# ==========================================
# 2. GÉNÉRATION DU FICHIER .BAT (INCLUANT IA)
# ==========================================
bat_content = """@echo off
title Titans Ecosystem Launcher
echo 🚀 Lancement de l'IA Service (Python)...
start cmd /k "cd titans-ai-service && venv\\Scripts\\activate && python start.py"
echo 🚀 Lancement du Bot Discord (Node)...
start cmd /k "cd titans-bot-core && npm run dev"
echo 🚀 Lancement de l'API Dashboard...
start cmd /k "cd titans-dashboard\\server && node index.js"
echo 🚀 Lancement du Client React (Vite)...
start cmd /k "cd titans-dashboard\\client && npm run dev"
echo ✨ Tout l'ecosystème Titans est en cours de démarrage...
"""

# ==========================================
# 3. CODE DU BOT (Events & Firebase)
# ==========================================
bot_index_js = """require('dotenv').config();
const { Client, GatewayIntentBits, Partials } = require('discord.js');
const fs = require('fs');
const path = require('path');
const { initFirebase, watchConfig } = require('./utils/firebase');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.GuildVoiceStates,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildModeration
    ],
    partials: [Partials.GuildMember, Partials.User]
});

initFirebase().then(() => client.login(process.env.DISCORD_TOKEN));

const eventsPath = path.join(__dirname, 'events');
if (fs.existsSync(eventsPath)) {
    const eventFiles = fs.readdirSync(eventsPath).filter(file => file.endsWith('.js'));
    for (const file of eventFiles) {
        const event = require(path.join(eventsPath, file));
        if (event.name) {
            if (event.once) client.once(event.name, (...args) => event.execute(...args));
            else client.on(event.name, (...args) => event.execute(...args));
        }
    }
}
"""

bot_event_voice = """const { Events, EmbedBuilder, AuditLogEvent } = require('discord.js');
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
                    embed.setDescription(`↔️ **${member.user.tag}** déplacé\\nDe: ${oldState.channel.toString()}\\nÀ: ${newState.channel.toString()}\\nPar: ${movedBy}`);
                    send = true;
                }
                if (send) chan.send({ embeds: [embed] }).catch(()=>{});
            }
        }
    }
};
"""

bot_event_ready = """const { Events, ActivityType } = require('discord.js');
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
"""

bot_firebase_js = """const { initializeApp } = require('firebase/app');
const { getFirestore, doc, onSnapshot } = require('firebase/firestore');
const { getAuth, signInAnonymously } = require('firebase/auth');

const firebaseConfig = {
  apiKey: process.env.FIREBASE_API_KEY,
  authDomain: process.env.FIREBASE_PROJECT_ID + ".firebaseapp.com",
  projectId: process.env.FIREBASE_PROJECT_ID,
  storageBucket: process.env.FIREBASE_PROJECT_ID + ".appspot.com",
  messagingSenderId: process.env.FIREBASE_SENDER_ID,
  appId: process.env.FIREBASE_APP_ID
};

const appId = 'titans-bot-prod';
let db;
const guildConfigs = new Map();

async function initFirebase() {
    try {
        const app = initializeApp(firebaseConfig);
        db = getFirestore(app);
        const auth = getAuth(app);
        await signInAnonymously(auth);
        console.log("✅ Firebase Bot Connecté");
    } catch (e) { console.error("❌ Erreur Firebase:", e.message); }
}

function watchConfig(guildId) {
    if (guildConfigs.has(guildId) || !db) return;
    onSnapshot(doc(db, 'artifacts', appId, 'public', 'data', 'guild_configs', guildId), (snap) => {
        if (snap.exists()) guildConfigs.set(guildId, snap.data());
    });
}

function getConfig(guildId) { return guildConfigs.get(guildId); }
module.exports = { initFirebase, watchConfig, getConfig };
"""

# ==========================================
# 4. DASHBOARD API SERVER
# ==========================================
server_index_js = """require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const app = express();

app.use(cors({ origin: 'http://localhost:5173', credentials: true }));
app.use(cookieParser());
app.use(express.json());

const DISCORD_API = 'https://discord.com/api/v10';
const AI_SERVICE_URL = 'http://localhost:8000'; // Port par défaut de AgentOS

app.get('/api/auth/login', (req, res) => {
    const url = `https://discord.com/oauth2/authorize?client_id=${process.env.DISCORD_CLIENT_ID}&redirect_uri=${encodeURIComponent(process.env.REDIRECT_URI)}&response_type=code&scope=identify%20guilds`;
    res.redirect(url);
});

app.get('/api/auth/callback', async (req, res) => {
    const { code } = req.query;
    if (!code) return res.status(400).send('Code manquant');
    try {
        const tokenResp = await axios.post(`${DISCORD_API}/oauth2/token`, new URLSearchParams({
            client_id: process.env.DISCORD_CLIENT_ID,
            client_secret: process.env.DISCORD_CLIENT_SECRET,
            grant_type: 'authorization_code',
            code: code,
            redirect_uri: process.env.REDIRECT_URI,
        }), { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
        res.cookie('access_token', tokenResp.data.access_token, { httpOnly: true });
        res.redirect('http://localhost:5173');
    } catch (e) { res.redirect('http://localhost:5173/?error=auth_failed'); }
});

app.post('/api/auth/logout', (req, res) => { res.clearCookie('access_token'); res.json({ ok: true }); });

// Proxy pour l'IA
app.post('/api/ai/ask', async (req, res) => {
    try {
        const { message } = req.body;
        const response = await axios.post(`${AI_SERVICE_URL}/chat`, { message });
        res.json({ answer: response.data.content });
    } catch (e) { 
        res.status(500).json({ error: "Service IA indisponible" }); 
    }
});

app.get('/api/user/guilds', async (req, res) => {
    const token = req.cookies.access_token;
    if(!token) return res.status(401).json({error: 'Non autorisé'});
    try {
        const user = await axios.get(`${DISCORD_API}/users/@me`, {headers:{Authorization:`Bearer ${token}`}});
        const guilds = await axios.get(`${DISCORD_API}/users/@me/guilds`, {headers:{Authorization:`Bearer ${token}`}});
        const adminGuilds = guilds.data.filter(g => (BigInt(g.permissions) & 0x8n) === 0x8n);
        const result = await Promise.all(adminGuilds.map(async g => {
            try { await axios.get(`${DISCORD_API}/guilds/${g.id}`, {headers:{Authorization:`Bot ${process.env.BOT_TOKEN}`}}); return {...g, botPresent:true}; }
            catch { return {...g, botPresent:false}; }
        }));
        res.json({user:user.data, guilds:result});
    } catch { res.status(500).json({error: 'Fail'}); }
});

app.get('/api/guilds/:id/channels', async (req, res) => {
    try {
        const ch = await axios.get(`${DISCORD_API}/guilds/${req.params.id}/channels`, {headers:{Authorization:`Bot ${process.env.BOT_TOKEN}`}});
        res.json(ch.data.filter(c => [0,2].includes(c.type)).map(c => ({id:c.id, name:c.name, type:c.type===2?'voice':'text'})));
    } catch { res.json([]); }
});

app.get('/api/guilds/:id/members', async (req, res) => {
    try {
        const m = await axios.get(`${DISCORD_API}/guilds/${req.params.id}/members?limit=1000`, {headers:{Authorization:`Bot ${process.env.BOT_TOKEN}`}});
        res.json(m.data.map(u => ({ id: u.user.id, tag: u.user.username, avatar: u.user.avatar })));
    } catch { res.json([]); }
});

app.post('/api/bot/embed/:guildId', async (req, res) => {
    try {
        const { channelId, embed } = req.body;
        const payload = { embeds: [{ title: embed.title, description: embed.description, color: parseInt((embed.color || "#5865f2").replace("#",""), 16) }] };
        if (embed.thumbnail) payload.embeds[0].thumbnail = { url: embed.thumbnail };
        if (embed.fields) payload.embeds[0].fields = embed.fields;
        await axios.post(`${DISCORD_API}/channels/${channelId}/messages`, payload, {headers:{Authorization:`Bot ${process.env.BOT_TOKEN}`}});
        res.json({ok:true});
    } catch { res.sendStatus(500); }
});

app.listen(3001, () => console.log('✅ API sur le port 3001'));
"""

# ==========================================
# 5. FRONTEND APP.JSX (VRAI COMPLET + IA + GIVEAWAY DESC)
# ==========================================
client_app_jsx = """
import React, { useState, useEffect } from 'react';
import { LayoutDashboard, Mic, Zap, Save, ArrowLeft, Plus, Trash2, CheckCircle, MessageSquare, Gift, Send, Loader2, Hash, Shield, Users, Search, Trophy, AlertCircle, Calendar, Clock, Check, Brain, Cpu } from 'lucide-react';
import { initializeApp } from 'firebase/app';
import { getFirestore, doc, getDoc, setDoc } from 'firebase/firestore';
import { getAuth, signInAnonymously } from 'firebase/auth';

const firebaseConfig = {
    apiKey: "___API_KEY___",
    authDomain: "___PROJECT_ID___.firebaseapp.com",
    projectId: "___PROJECT_ID___",
    storageBucket: "___PROJECT_ID___.appspot.com",
    messagingSenderId: "___SENDER_ID___",
    appId: "___APP_ID___"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);
const appId = 'titans-bot-prod';

const Card = ({children, className=""}) => <div className={`bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-4 shadow-xl ${className}`}>{children}</div>;
const Button = ({children, onClick, variant='primary', disabled=false, className=''}) => {
    const vars = { 
        primary: 'bg-indigo-600 hover:bg-indigo-500 shadow-indigo-600/20 shadow-lg', 
        secondary: 'bg-zinc-800 hover:bg-zinc-700 border border-zinc-700', 
        success: 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-600/20 shadow-lg', 
        gold: 'bg-gradient-to-br from-amber-400 to-amber-600 text-black font-black uppercase tracking-tighter' 
    };
    return <button onClick={onClick} disabled={disabled} className={`px-4 py-2 rounded-xl font-bold text-white transition-all flex items-center justify-center gap-2 ${vars[variant]||vars.primary} ${disabled?'opacity-50 cursor-not-allowed':''} ${className}`}>{children}</button>;
};

const Input = ({label, value, onChange, placeholder, type='text'}) => (
    <div className="space-y-1.5 w-full"><label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest">{label}</label>
    <input type={type} value={value} onChange={onChange} placeholder={placeholder} className="w-full bg-zinc-950 border border-zinc-800 rounded-xl py-3 px-4 text-sm text-white focus:ring-2 ring-indigo-500 outline-none transition-all"/></div>
);

const Select = ({label, value, onChange, options}) => (
    <div className="space-y-1.5 w-full"><label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest">{label}</label>
    <select value={value} onChange={onChange} className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-sm text-white outline-none cursor-pointer">
        <option value="">Sélectionner...</option>{(options || []).map(o=><option key={o.id} value={o.id}>{o.name}</option>)}
    </select></div>
);

const Toggle = ({label, checked, onChange}) => (
    <div className="flex justify-between items-center p-4 bg-zinc-950/50 rounded-xl border border-zinc-800 cursor-pointer hover:bg-zinc-900 transition-all" onClick={()=>onChange(!checked)}>
        <span className="text-sm text-zinc-400 font-bold">{label}</span>
        <div className={`w-11 h-6 rounded-full relative transition-colors ${checked?'bg-indigo-600':'bg-zinc-800'}`}>
            <div className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${checked?'translate-x-5':'translate-x-0'}`} />
        </div>
    </div>
);

// --- MODULE IA ---
const AIModule = () => {
    const [query, setQuery] = useState("");
    const [response, setResponse] = useState("");
    const [loading, setLoading] = useState(false);

    const askAI = async () => {
        if(!query) return;
        setLoading(true);
        try {
            const res = await fetch('/api/ai/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: query })
            });
            const data = await res.json();
            setResponse(data.answer);
        } catch (e) { setResponse("Erreur : Service IA non connecté."); }
        finally { setLoading(false); }
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <Card className="border-indigo-500/20">
                <h3 className="text-sm font-black text-white flex gap-2 mb-6 uppercase tracking-widest items-center"><Brain className="text-indigo-400"/> Assistant Titans (Warframe & Riven)</h3>
                <div className="flex gap-4">
                    <Input placeholder="Posez une question sur Warframe, les Rivens ou le Clan..." value={query} onChange={e=>setQuery(e.target.value)} />
                    <Button onClick={askAI} disabled={loading} className="px-8">{loading ? <Loader2 className="animate-spin"/> : <Send size={18}/>}</Button>
                </div>
            </Card>
            {response && (
                <Card className="bg-zinc-950 border-indigo-500/10">
                    <div className="text-xs font-black text-indigo-400 uppercase tracking-widest mb-4 flex items-center gap-2"><Cpu size={14}/> Réponse de Titans AI</div>
                    <div className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">{response}</div>
                </Card>
            )}
        </div>
    );
};

// --- MODULE GIVEAWAY ---
const GiveawayModule = ({ guild, channels }) => {
    const [members, setMembers] = useState([]);
    const [search, setSearch] = useState('');
    const [selected, setSelected] = useState([]);
    const [winner, setWinner] = useState(null);
    const [rolling, setRolling] = useState(false);
    const [config, setConfig] = useState({ title: 'GIVEAWAY TITAN', prize: 'Nitro 1 Mois', desc: 'Participez à notre événement clanique !', endDate: '', chan: '' });

    useEffect(() => { fetch(`/api/guilds/${guild.id}/members`).then(r => r.json()).then(setMembers); }, [guild.id]);

    const pick = () => {
        const pool = selected.length > 0 ? members.filter(m => selected.includes(m.id)) : members;
        if (pool.length === 0) return alert("Aucun membre disponible !");
        setRolling(true);
        let count = 0;
        const interval = setInterval(() => {
            setWinner(pool[Math.floor(Math.random() * pool.length)]);
            count++;
            if (count > 20) { clearInterval(interval); setRolling(false); }
        }, 80);
    };

    const publish = async () => {
        if (!config.chan) return alert("Sélectionnez un salon !");
        const ts = config.endDate ? Math.floor(new Date(config.endDate).getTime() / 1000) : null;
        const embed = { 
            title: `🎁 GIVEAWAY : ${config.title}`, 
            description: `**Lot:** ${config.prize}\\n\\n${config.desc}\\n\\n${ts ? `**Fin de l'événement:** <t:${ts}:R>` : "Pas de date de fin"}`, 
            color: "#f1c40f",
            fields: [{ name: "Candidats", value: `${selected.length || members.length} membres` }]
        };
        await fetch(`/api/bot/embed/${guild.id}`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({channelId:config.chan, embed})});
        alert("Giveaway envoyé !");
    };

    return (
        <div className="grid lg:grid-cols-12 gap-8 animate-in fade-in duration-500">
            <div className="lg:col-span-8 space-y-6">
                <Card>
                    <h3 className="text-sm font-black text-white flex gap-2 mb-6 uppercase tracking-widest items-center"><Calendar className="text-indigo-400"/> Paramètres du Tirage</h3>
                    <div className="grid md:grid-cols-2 gap-4">
                        <Input label="Titre de l'Event" value={config.title} onChange={e=>setConfig({...config, title:e.target.value})} />
                        <Input label="Lot à Gagner" value={config.prize} onChange={e=>setConfig({...config, prize:e.target.value})} />
                    </div>
                    <div className="space-y-1.5 w-full">
                        <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest">Description de l'Événement</label>
                        <textarea className="w-full bg-zinc-950 border border-zinc-800 rounded-xl p-4 text-sm text-white focus:ring-2 ring-indigo-500 outline-none h-24" value={config.desc} onChange={e=>setConfig({...config, desc:e.target.value})} placeholder="Règles, conditions, etc..." />
                    </div>
                    <div className="grid md:grid-cols-2 gap-4">
                        <Input label="Date de Fin" type="datetime-local" value={config.endDate} onChange={e=>setConfig({...config, endDate:e.target.value})} />
                        <Select label="Salon d'Annonce" options={channels.filter(c=>c.type==='text')} value={config.chan} onChange={e=>setConfig({...config, chan:e.target.value})} />
                    </div>
                    <Button onClick={publish} className="w-full py-4 mt-2" variant="primary">Publier l'Annonce Discord</Button>
                </Card>

                <Card className="h-[400px] flex flex-col">
                    <h3 className="text-sm font-black text-white uppercase mb-4 tracking-widest">Participants ({selected.length || 'Tous'})</h3>
                    <Input placeholder="Rechercher un membre..." value={search} onChange={e=>setSearch(e.target.value)} />
                    <div className="flex-1 bg-zinc-950 rounded-xl mt-4 overflow-auto p-2 border border-zinc-800 grid grid-cols-2 md:grid-cols-3 gap-2">
                        {members.filter(m=>m.tag.toLowerCase().includes(search.toLowerCase())).map(m=>(
                            <div key={m.id} onClick={()=>setSelected(s=>s.includes(m.id)?s.filter(x=>x!==m.id):[...s, m.id])} className={`p-3 rounded-xl cursor-pointer border transition-all flex items-center gap-2 ${selected.includes(m.id)?'bg-indigo-600/20 border-indigo-500 text-white shadow-lg shadow-indigo-500/10':'bg-zinc-900 border-zinc-800 text-zinc-400 hover:bg-zinc-800'}`}>
                                <div className="w-7 h-7 rounded-full bg-zinc-800 flex items-center justify-center text-[10px] overflow-hidden">
                                    {m.avatar ? <img src={`https://cdn.discordapp.com/avatars/${m.id}/${m.avatar}.png`} /> : m.tag[0]}
                                </div>
                                <span className="text-[10px] font-bold truncate">{m.tag}</span>
                                {selected.includes(m.id) && <Check size={14} className="ml-auto text-indigo-400" />}
                            </div>
                        ))}
                    </div>
                </Card>
            </div>
            
            <div className="lg:col-span-4 space-y-6">
                <Card className="flex flex-col items-center justify-center py-12 border-amber-500/20 bg-gradient-to-br from-amber-500/5 to-transparent">
                    <Trophy size={48} className="text-amber-500 mb-6 drop-shadow-[0_0_10px_rgba(245,158,11,0.5)]" />
                    <h4 className="text-xs font-black text-amber-500 uppercase tracking-widest mb-10">Tirage Aléatoire</h4>
                    {winner ? (
                        <div className="text-center animate-in zoom-in duration-300">
                            <div className="w-32 h-32 rounded-full border-4 border-amber-500 shadow-2xl mx-auto overflow-hidden mb-6 p-1 bg-zinc-900">
                                {winner.avatar ? <img src={`https://cdn.discordapp.com/avatars/${winner.id}/${winner.avatar}.png`} className="w-full h-full object-cover rounded-full" /> : <div className="w-full h-full flex items-center justify-center text-4xl font-black">{winner.tag[0]}</div>}
                            </div>
                            <h4 className="text-2xl font-black text-white tracking-tighter">{winner.tag}</h4>
                            <p className="text-zinc-500 text-[10px] font-bold mt-1 uppercase tracking-widest">Le grand gagnant !</p>
                        </div>
                    ) : <span className="text-zinc-700 font-black uppercase text-[10px] tracking-widest">Prêt pour le tirage</span>}
                    <Button onClick={pick} variant="gold" disabled={rolling} className="w-full mt-12 py-5 text-sm tracking-widest">
                        {rolling ? "ROULEMENT..." : "LANCER LE TIRAGE"}
                    </Button>
                </Card>
            </div>
        </div>
    );
};

export default function App() {
    const [user, setUser] = useState(null);
    const [guilds, setGuilds] = useState([]);
    const [currentGuild, setCurrentGuild] = useState(null);
    const [channels, setChannels] = useState([]);
    const [config, setConfig] = useState({});
    const [module, setModule] = useState('overview');
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [hasChanges, setHasChanges] = useState(false);

    useEffect(() => {
        signInAnonymously(auth);
        fetch('/api/user/guilds').then(r => r.json()).then(d => { 
            if(d.user) { setUser(d.user); setGuilds(d.guilds || []); }
        });
    }, []);

    const select = async (g) => {
        setLoading(true);
        try {
            const [ch, snap] = await Promise.all([
                fetch(`/api/guilds/${g.id}/channels`).then(r=>r.json()).catch(()=>[]),
                getDoc(doc(db, 'artifacts', appId, 'public', 'data', 'guild_configs', g.id)).catch(()=>null)
            ]);
            setChannels(ch || []);
            setConfig(snap?.exists() ? snap.data() : {});
            setCurrentGuild(g);
            setHasChanges(false);
            setModule('overview');
        } finally { setLoading(false); }
    };

    const update = (k, v) => { setConfig({...config, [k]: v}); setHasChanges(true); };

    const save = async () => {
        setSaving(true);
        try {
            await setDoc(doc(db, 'artifacts', appId, 'public', 'data', 'guild_configs', currentGuild.id), config, {merge:true});
            setHasChanges(false);
            alert("✅ Données sauvegardées sur le Cloud !");
        } catch (e) { alert(e.message); }
        finally { setSaving(false); }
    };

    if(!user) return (
        <div className="min-h-screen bg-black flex flex-col items-center justify-center p-6 text-white font-sans">
            <h1 className="text-5xl font-black italic text-indigo-500 mb-10 tracking-tighter">TITANS</h1>
            <Button onClick={()=>window.location.href='/api/auth/login'} className="py-6 px-12 text-xl shadow-2xl">SE CONNECTER AVEC DISCORD</Button>
        </div>
    );

    if(!currentGuild) return (
        <div className="min-h-screen bg-black p-12 text-white font-sans text-center">
            <h1 className="text-4xl font-black tracking-tighter mb-16 italic text-indigo-500">TITANS DASHBOARD</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
                {guilds.map(g => (
                    <button key={g.id} onClick={()=>select(g)} className={`group p-10 rounded-[2.5rem] border border-zinc-800 bg-zinc-900/40 hover:bg-zinc-900 hover:border-indigo-500/50 transition-all flex flex-col items-center gap-6 ${!g.botPresent && 'opacity-40 grayscale pointer-events-none'}`}>
                        <div className="w-24 h-24 bg-zinc-800 rounded-[2.5rem] flex items-center justify-center text-4xl font-black group-hover:scale-110 transition-transform">
                            {g.name[0]}
                        </div>
                        <div className="font-black text-xl tracking-tight">{g.name}</div>
                        <div className="text-[10px] uppercase font-black text-indigo-500 tracking-widest">{g.botPresent ? "Gérer le Serveur" : "Bot Absent"}</div>
                    </button>
                ))}
            </div>
        </div>
    );

    if(loading) return <div className="min-h-screen bg-black flex flex-col items-center justify-center gap-6"><Loader2 className="animate-spin text-indigo-500" size={56}/><p className="font-black uppercase text-[10px] tracking-widest text-zinc-500">Chargement du serveur...</p></div>;

    return (
        <div className="min-h-screen bg-black flex text-white font-sans antialiased overflow-hidden">
            <aside className="w-72 border-r border-zinc-800 p-8 flex flex-col gap-2 bg-zinc-950/40 backdrop-blur-3xl shrink-0">
                <span className="text-3xl font-black tracking-tighter text-indigo-500 italic mb-12">TITANS</span>
                <Button variant="secondary" onClick={()=>setCurrentGuild(null)} className="mb-10 py-3.5 text-[10px] uppercase font-black tracking-widest"><ArrowLeft size={16}/> Changer Serveur</Button>
                <div className="space-y-1">
                    <NavBtn id="overview" label="Vue d'ensemble" icon={LayoutDashboard} active={module} set={setModule} />
                    <div className="h-px bg-zinc-900 mx-4 my-8 opacity-40" />
                    <NavBtn id="ai" label="IA Titans" icon={Brain} active={module} set={setModule} />
                    <NavBtn id="voice" label="Logs Vocaux" icon={Mic} active={module} set={setModule} />
                    <NavBtn id="triggers" label="Role Triggers" icon={Zap} active={module} set={setModule} />
                    <NavBtn id="giveaway" label="Giveaways Pro" icon={Trophy} active={module} set={setModule} />
                    <NavBtn id="embed" label="Embed Builder" icon={MessageSquare} active={module} set={setModule} />
                </div>
            </aside>
            <main className="flex-1 p-14 overflow-y-auto">
                <header className="flex justify-between items-center mb-14 bg-zinc-900/40 p-6 rounded-[2rem] border border-zinc-800 backdrop-blur shadow-2xl">
                    <h1 className="text-3xl font-black tracking-tighter leading-none">{currentGuild.name}</h1>
                    <Button onClick={save} disabled={!hasChanges || saving} variant={hasChanges ? "success" : "secondary"} className="px-10 py-4">
                        {saving ? <Loader2 className="animate-spin" size={20}/> : <Save size={20}/>} {hasChanges ? "SAUVEGARDER" : "À JOUR"}
                    </Button>
                </header>
                <div className="max-w-6xl mx-auto">
                    {module==='overview' && <div className="grid grid-cols-3 gap-6"><Card className="border-l-4 border-indigo-500 p-8"><h4 className="text-[10px] font-black uppercase text-zinc-500 mb-2">Salons Totaux</h4><div className="text-3xl font-black">{channels.length}</div></Card></div>}
                    {module==='ai' && <AIModule />}
                    {module==='giveaway' && <GiveawayModule guild={currentGuild} channels={channels} />}
                    {module==='voice' && (
                        <Card>
                            <h3 className="text-sm font-black uppercase tracking-widest mb-6 flex gap-2"><Mic className="text-indigo-500"/> Configuration Logs</h3>
                            <Select label="Salon Logs" options={channels.filter(c=>c.type==='text')} value={config.voiceLogs?.channelId||''} onChange={e=>update('voiceLogs', {...config.voiceLogs, channelId:e.target.value})} />
                            <div className="grid grid-cols-3 gap-4 mt-8">
                                <Toggle label="ID Utilisateur" checked={config.voiceLogs?.showId} onChange={v=>update('voiceLogs', {...config.voiceLogs, showId:v})} />
                                <Toggle label="Avatar Profil" checked={config.voiceLogs?.showAvatar} onChange={v=>update('voiceLogs', {...config.voiceLogs, showAvatar:v})} />
                                <Toggle label="Audit Log (Responsable)" checked={config.voiceLogs?.showResponsible} onChange={v=>update('voiceLogs', {...config.voiceLogs, showResponsible:v})} />
                            </div>
                            <div className="grid grid-cols-3 gap-4 mt-4">
                                <Toggle label="Logger Joins" checked={config.voiceLogs?.join} onChange={v=>update('voiceLogs', {...config.voiceLogs, join:v})} />
                                <Toggle label="Logger Leaves" checked={config.voiceLogs?.leave} onChange={v=>update('voiceLogs', {...config.voiceLogs, leave:v})} />
                                <Toggle label="Logger Moves" checked={config.voiceLogs?.move} onChange={v=>update('voiceLogs', {...config.voiceLogs, move:v})} />
                            </div>
                        </Card>
                    )}
                    {module==='triggers' && (
                        <div className="space-y-4">
                            <Button onClick={()=>update('triggers', [...(config.triggers||[]), {id:Date.now(), voiceId:'', channelId:'', message:'Salut {user} !', ghostPing:false}])} className="w-full py-4 uppercase font-black tracking-widest text-xs shadow-indigo-500/20 shadow-xl"><Plus size={16}/> Nouveau Trigger</Button>
                            {(config.triggers||[]).map(t => (
                                <Card key={t.id} className="relative group border-l-4 border-l-transparent hover:border-l-indigo-500 transition-all">
                                    <button onClick={()=>update('triggers', config.triggers.filter(x=>x.id!==t.id))} className="absolute top-4 right-4 text-zinc-700 hover:text-rose-500 transition-colors"><Trash2 size={20}/></button>
                                    <div className="grid md:grid-cols-2 gap-4">
                                        <Select label="Salon Vocal" options={channels.filter(c=>c.type==='voice')} value={t.voiceId} onChange={e=>update('triggers', config.triggers.map(x=>x.id===t.id?{...x, voiceId:e.target.value}:x))} />
                                        <Select label="Salon Texte" options={channels.filter(c=>c.type==='text')} value={t.channelId} onChange={e=>update('triggers', config.triggers.map(x=>x.id===t.id?{...x, channelId:e.target.value}:x))} />
                                    </div>
                                    <Input label="Message ({user}, {voice})" value={t.message} onChange={e=>update('triggers', config.triggers.map(x=>x.id===t.id?{...x, message:e.target.value}:x))} />
                                    <Toggle label="Ghost Ping (Mention sans notif)" checked={t.ghostPing} onChange={v=>update('triggers', config.triggers.map(x=>x.id===t.id?{...x, ghostPing:v}:x))} />
                                </Card>
                            ))}
                        </div>
                    )}
                    {module==='embed' && (
                        <div className="grid md:grid-cols-2 gap-8">
                             <Card>
                                <Select label="Destination" options={channels.filter(c=>c.type==='text')} value={config.embedBuilder?.channelId||''} onChange={e=>update('embedBuilder', {...config.embedBuilder, channelId:e.target.value})} />
                                <Input label="Titre" value={config.embedBuilder?.title||''} onChange={e=>update('embedBuilder', {...config.embedBuilder, title:e.target.value})} />
                                <textarea className="w-full bg-zinc-950 border border-zinc-800 rounded-xl p-4 text-sm mt-4 text-white focus:ring-2 ring-indigo-500 outline-none h-32" placeholder="Description..." value={config.embedBuilder?.desc||''} onChange={e=>update('embedBuilder', {...config.embedBuilder, desc:e.target.value})} />
                                <Input label="Couleur Hex" value={config.embedBuilder?.color||'#5865F2'} onChange={e=>update('embedBuilder', {...config.embedBuilder, color:e.target.value})} />
                                <Button onClick={async () => {
                                    await fetch(`/api/bot/embed/${currentGuild.id}`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({channelId:config.embedBuilder.channelId, embed:{title:config.embedBuilder.title, description:config.embedBuilder.desc, color:config.embedBuilder.color}})});
                                    alert("Envoyé !");
                                }} className="w-full py-4 mt-4 font-black">ENVOYER L'EMBED</Button>
                            </Card>
                            <div className="bg-[#313338] p-6 rounded-[2rem] border border-zinc-800 shadow-2xl h-fit">
                                <div className="flex gap-4 mb-4"><div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center font-black">T</div><div><p className="font-bold text-sm">Titans Bot</p><p className="text-[10px] text-zinc-500">Aujourd'hui</p></div></div>
                                <div className="mt-1 border-l-4 bg-[#2b2d31] p-4 rounded-r-lg" style={{borderLeftColor: config.embedBuilder?.color || '#5865F2'}}>
                                    <p className="font-bold text-white mb-1">{config.embedBuilder?.title || 'Titre'}</p>
                                    <p className="text-zinc-300 text-sm whitespace-pre-wrap">{config.embedBuilder?.desc || 'Description...'}</p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}

const NavBtn = ({id, label, icon:Icon, active, set}) => (
    <button onClick={()=>set(id)} className={`flex items-center gap-4 px-6 py-4 rounded-2xl transition-all font-black group relative ${active===id?'bg-indigo-600 text-white shadow-2xl shadow-indigo-600/30 -translate-y-1':'text-zinc-500 hover:text-white hover:bg-zinc-900/60'}`}>
        <Icon size={19} className={`${active===id?'text-white':'text-zinc-700 group-hover:text-indigo-500'} transition-colors`} />
        <span className="text-[11px] uppercase tracking-wider">{label}</span>
    </button>
);
""".replace("___API_KEY___", fb_api_key).replace("___PROJECT_ID___", fb_project_id).replace("___SENDER_ID___", fb_sender_id).replace("___APP_ID___", fb_app_id)

# ==========================================
# 6. CODE DU SERVICE IA (IMPORTÉ DU ZIP)
# ==========================================

ai_instructions_py = """# instructions.py
WARFRAME_AGENT_INSTRUCTIONS = [
    "Tu es un expert du gameplay de Warframe, des mécaniques, des builds et du lore.",
    "Utilise ta base de connaissances pour répondre aux questions.",
    "Cite TOUJOURS tes sources en mentionnant le nom du document.",
    "Réponds en FRANCAIS avec un ton aidant et semi-militaire (appelle l'utilisateur Tenno)."
]

CLAN_AGENT_INSTRUCTIONS = [
    "Tu es le gardien des connaissances du Clan Titans Primes.",
    "Utilise ta base de connaissances pour répondre aux questions sur les règles, la hiérarchie et l'histoire du clan."
]

RIVEN_AGENT_INSTRUCTIONS = [
    "Tu es un expert de l'économie des Rivens dans Warframe.",
    "Estime les prix en fonction des statistiques fournies.",
    "Sois honnête : si un Riven est mauvais, dis qu'il faut le relancer (Trash)."
]

TITAN_BOT_INSTRUCTIONS = [
    "Tu es le cerveau central du bot Titans Primes.",
    "Tu coordonnes les agents spécialisés (Warframe, Clan, Riven).",
    "Réponds toujours poliment et en français."
]
"""

ai_config_py = f"""# config.py
import os
from agno.models.openai import OpenAIResponses
from agno.knowledge.embedder.openai import OpenAIEmbedder
from dotenv import load_dotenv

load_dotenv()

embedder = OpenAIEmbedder(id="text-embedding-3-small")
model = OpenAIResponses(id="gpt-4o-mini")

PG_USER = os.getenv("PG_USER", "ai")
PG_PASSWORD = os.getenv("PG_PASSWORD", "ai")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5532")
PG_DBNAME = os.getenv("PG_DBNAME", "ai")

db_url = f"postgresql+psycopg://{{PG_USER}}:{{PG_PASSWORD}}@{{PG_HOST}}:{{PG_PORT}}/{{PG_DBNAME}}"
"""

ai_titan_bot_py = """# titan_bot.py
from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector
from agno.db.postgres import PostgresDb
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.csv_toolkit import CsvTools
from agno.tools.calculator import CalculatorTools
from agno.team import Team

from config import db_url, model, embedder
from instructions import *

warframe_knowledge = Knowledge(
    vector_db=PgVector(table_name="warframe_vectors", db_url=db_url, embedder=embedder),
    contents_db=PostgresDb(id="warframe_contents_db", db_url=db_url, knowledge_table="warframe_contents"),
)

clan_knowledge = Knowledge(
    vector_db=PgVector(table_name="clan_vectors", db_url=db_url, embedder=embedder),
    contents_db=PostgresDb(id="clan_contents_db", db_url=db_url, knowledge_table="clan_contents"),
)

warframe_agent = Agent(
    name="Warframe Agent",
    model=model,
    knowledge=warframe_knowledge,
    tools=[CalculatorTools()],
    instructions=WARFRAME_AGENT_INSTRUCTIONS,
)

clan_agent = Agent(
    name="Clan Agent",
    model=model,
    knowledge=clan_knowledge,
    instructions=CLAN_AGENT_INSTRUCTIONS,
)

riven_agent = Agent(
    name="Riven Agent",
    model=model,
    tools=[CsvTools(csvs=["csv/riven_sales.csv", "csv/weapon_info.csv"]), CalculatorTools()],
    instructions=RIVEN_AGENT_INSTRUCTIONS,
)

titan_bot_team = Team(
    name="Titans AI Core",
    agents=[warframe_agent, clan_agent, riven_agent],
    instructions=TITAN_BOT_INSTRUCTIONS,
)
"""

ai_start_py = """# start.py
import os
from agno.os import AgentOS
from titan_bot import titan_bot_team

agent_os = AgentOS(
    id="titan-bot-os",
    teams=[titan_bot_team],
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="start:app", port=8000)
"""

ai_ingest_py = """# ingest_knowledge.py
import os
from agno.knowledge.reader.text_reader import TextReader
from agno.knowledge.reader.csv_reader import CSVReader
from titan_bot import warframe_knowledge, clan_knowledge

def load_knowledge():
    print("🚀 Ingestion de la base de connaissances...")
    if os.path.exists("knowledge/warframe"):
        warframe_knowledge.load_documents(path="knowledge/warframe", reader=TextReader(chunk=True))
    if os.path.exists("knowledge/clan"):
        clan_knowledge.load_documents(path="knowledge/clan", reader=TextReader(chunk=True))
    print("✅ Ingestion terminée !")

if __name__ == "__main__":
    load_knowledge()
"""

# ==========================================
# 7. ÉCRITURE DES FICHIERS
# ==========================================
def write_file(path, content):
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Fichier : {path}")

print("🚀 Reconstruction intégrale avec IA Intégrée...")

# Bot
write_file(f"{bot_dir}/index.js", bot_index_js)
write_file(f"{bot_dir}/utils/firebase.js", bot_firebase_js)
write_file(f"{bot_dir}/events/voice.js", bot_event_voice)
write_file(f"{bot_dir}/events/ready.js", bot_event_ready)

# Dashboard
write_file(f"{dashboard_dir}/server/index.js", server_index_js)
write_file(f"{dashboard_dir}/client/src/App.jsx", client_app_jsx)

# AI Service
write_file(f"{ai_dir}/config.py", ai_config_py)
write_file(f"{ai_dir}/instructions.py", ai_instructions_py)
write_file(f"{ai_dir}/titan_bot.py", ai_titan_bot_py)
write_file(f"{ai_dir}/ingest_py.py", ai_ingest_py)
write_file(f"{ai_dir}/start.py", ai_start_py)
write_file(f"{ai_dir}/requirements.txt", "agno\\npsycopg[binary]\\nsqlalchemy\\ndotenv\\npydantic\\nopenai")

# Launcher
write_file("start_dev.bat", bat_content)

print("\\n✨ PROJET RESTAURÉ & IA INTÉGRÉE !")
print("👉 Important : Crée les dossiers 'csv' et 'knowledge' dans 'titans-ai-service' et place tes fichiers de 42mo dedans.")
print("👉 Puis lance 'start_dev.bat'.")