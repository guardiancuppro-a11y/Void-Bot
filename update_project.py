import os

# Configuration des dossiers
dashboard_dir = "titans-dashboard"
bot_dir = "titans-bot-core"
ai_dir = "titans-ai-service"

# ==========================================
# 0. RÉCUPÉRATION DES CLÉS (.env)
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
discord_client_id = env_vars.get("DISCORD_CLIENT_ID", "TON_CLIENT_ID")
discord_client_secret = env_vars.get("DISCORD_CLIENT_SECRET", "TON_CLIENT_SECRET")
bot_token = env_vars.get("BOT_TOKEN", "TON_BOT_TOKEN")

# ==========================================
# 1. GÉNÉRATION DU FICHIER .BAT
# ==========================================
bat_content = """@echo off
title Titans Prime Ecosystem
echo 🚀 Lancement de l'IA Service...
start cmd /k "cd titans-ai-service && python start.py"
echo 🚀 Lancement du Bot Discord...
start cmd /k "cd titans-bot-core && npm run dev"
echo 🚀 Lancement de l'API Dashboard...
start cmd /k "cd titans-dashboard\\server && node index.js"
echo 🚀 Lancement du Dashboard Prime (Vite)...
start cmd /k "cd titans-dashboard\\client && npm run dev"
echo ✨ Ecosystem Titans Prime opérationnel.
"""

# ==========================================
# 2. CODE DU DASHBOARD (FRONTEND - OPTIMISÉ)
# ==========================================
client_app_jsx = """
import React, { useState, useEffect, useMemo } from 'react';
import { 
  LayoutDashboard, Mic, Zap, Save, ArrowLeft, Plus, Trash2, 
  MessageSquare, Send, Loader2, Hash, Shield, Users, Trophy, 
  Brain, Cpu, Star, Rocket, ShieldCheck, ChevronRight, Home, 
  ShieldAlert, LogOut, Activity, Settings, Bell, Globe, Search,
  Clock, Target, Image as ImageIcon, CheckSquare, X, History,
  Gavel, UserX, UserMinus, VolumeX, AlertTriangle, Repeat, Users as UsersIcon,
  Palette, Type, Layers, Square, MousePointer2
} from 'lucide-react';
import { initializeApp } from 'firebase/app';
import { getFirestore, doc, getDoc, setDoc } from 'firebase/firestore';
import { getAuth, signInAnonymously, onAuthStateChanged, signInWithCustomToken } from 'firebase/auth';

// --- CONFIGURATION ---
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
const CLIENT_ID = "___CLIENT_ID___";

const THEME = {
    primary: "#fdc72e",      
    bgMain: "#0f0f0f",       
    bgCard: "#050505",       
    radius: "rounded-none",
};

// --- COMPOSANTS UI ---

const Title = ({ children, level = 1, className = "" }) => {
  const sizes = {
    1: "text-7xl font-black italic tracking-tighter uppercase leading-[0.8]",
    2: "text-4xl font-black italic tracking-tighter uppercase leading-none",
    3: "text-[10px] font-black uppercase tracking-[0.5em] text-[#fdc72e]",
  };
  return <h2 className={`${sizes[level]} ${className}`}>{children}</h2>;
};

const Card = ({ children, title, className = "" }) => (
  <div className={`bg-[#050505] border border-zinc-900 rounded-none p-10 text-left transition-colors hover:border-zinc-800 ${className}`}>
    {title && <Title level={3} className="mb-8 border-b border-zinc-900 pb-4">{title}</Title>}
    {children}
  </div>
);

const ActionButton = ({ children, onClick, variant = 'gold', icon: Icon, disabled, className = "" }) => {
  const styles = {
    gold: "bg-[#fdc72e] text-black hover:bg-white",
    outline: "bg-transparent text-zinc-500 border border-zinc-800 hover:border-white hover:text-white",
    danger: "text-red-500 border border-red-900/30 hover:bg-red-500 hover:text-white",
    subtle: "text-zinc-600 hover:text-[#fdc72e] bg-transparent"
  };
  return (
    <button 
      onClick={onClick} disabled={disabled}
      className={`px-8 py-4 rounded-none font-black uppercase tracking-[0.2em] text-[10px] flex items-center gap-4 transition-all active:scale-95 disabled:opacity-20 border-none cursor-pointer italic ${styles[variant]} ${className}`}
    >
      {Icon && <Icon size={14} />}
      {children}
    </button>
  );
};

const Input = ({ label, value, onChange, placeholder, type = 'text', rows }) => (
  <div className="flex flex-col gap-3 w-full text-left mb-8">
    {label && <label className="text-[9px] font-black text-zinc-700 uppercase tracking-[0.4em] ml-1">{label}</label>}
    {rows ? (
      <textarea rows={rows} value={value} onChange={onChange} placeholder={placeholder} className="bg-[#0f0f0f] border border-zinc-900 p-5 text-white text-sm focus:border-[#fdc72e] outline-none rounded-none placeholder:text-zinc-800 resize-none font-medium" />
    ) : (
      <input type={type} value={value} onChange={onChange} placeholder={placeholder} className="bg-[#0f0f0f] border border-zinc-900 p-5 text-white text-sm focus:border-[#fdc72e] outline-none rounded-none placeholder:text-zinc-800 font-medium" />
    )}
  </div>
);

const Select = ({ label, value, onChange, options }) => (
  <div className="flex flex-col gap-3 w-full text-left mb-8">
    {label && <label className="text-[9px] font-black text-zinc-700 uppercase tracking-[0.4em] ml-1">{label}</label>}
    <select value={value} onChange={onChange} className="bg-[#0f0f0f] border border-zinc-900 p-5 text-white text-sm focus:border-[#fdc72e] outline-none rounded-none cursor-pointer appearance-none">
        <option value="">SÉLECTIONNER...</option>
        {(options || []).map(o => <option key={o.id} value={o.id}>{o.name}</option>)}
    </select>
  </div>
);

const Toggle = ({ label, checked, onChange }) => (
  <div className="flex justify-between items-center p-6 bg-[#0f0f0f] border border-zinc-900 rounded-none cursor-pointer hover:border-zinc-700 transition-all mb-4" onClick={() => onChange(!checked)}>
    <span className="text-[10px] font-black text-zinc-500 uppercase tracking-[0.3em]">{label}</span>
    <div className={`w-12 h-5 rounded-none relative transition-all ${checked ? 'bg-[#fdc72e]' : 'bg-zinc-800'}`}>
        <div className={`absolute top-1 left-1 bg-white w-3 h-3 rounded-none transition-transform ${checked ? 'translate-x-7' : 'translate-x-0'}`} />
    </div>
  </div>
);

// --- MODULES ---

const Overview = ({ guild, channels }) => (
  <div className="animate-in fade-in duration-700 text-left">
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-1 mb-20">
      <div className="border border-zinc-900 p-12 bg-zinc-950/20">
        <p className="text-[10px] font-black text-[#fdc72e] uppercase tracking-[0.6em] mb-6 italic">Personnel</p>
        <p className="text-8xl font-black text-white leading-none tracking-tighter italic">{guild.approximate_member_count || '---'}</p>
        <p className="text-zinc-700 text-[10px] font-bold mt-6 uppercase tracking-widest">Unités Tenno</p>
      </div>
      <div className="border border-zinc-900 p-12 bg-zinc-950/20">
        <p className="text-[10px] font-black text-zinc-700 uppercase tracking-[0.6em] mb-6">Nexus</p>
        <p className="text-8xl font-black text-white leading-none tracking-tighter italic">{channels.length}</p>
        <p className="text-zinc-700 text-[10px] font-bold mt-6 uppercase tracking-widest">Liaisons Actives</p>
      </div>
      <div className="border border-zinc-900 p-12 bg-zinc-950/20">
        <p className="text-[10px] font-black text-zinc-700 uppercase tracking-[0.6em] mb-6">Boosts</p>
        <p className="text-8xl font-black text-white leading-none tracking-tighter italic">{guild.premium_subscription_count || '0'}</p>
        <p className="text-[#fdc72e] text-[10px] font-bold mt-6 uppercase tracking-widest">Surcharges Prime</p>
      </div>
    </div>
  </div>
);

const AIModule = () => {
  const [q, setQ] = useState("");
  const [ans, setAns] = useState("");
  const [load, setLoad] = useState(false);
  const ask = async () => {
    if(!q) return; setLoad(true);
    try {
      const r = await fetch('/api/ai/ask', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ message: q }) });
      const d = await r.json(); setAns(d.answer);
    } catch { setAns("Liaison interrompue."); } finally { setLoad(false); }
  };
  return (
    <div className="animate-in fade-in duration-700 text-left">
      <div className="flex flex-col md:flex-row gap-10 items-start mb-20">
        <div className="flex-1 w-full">
            <Title level={3} className="mb-6">Interrogation Céphalon</Title>
            <Input placeholder="Builds, Lore, Rivens... Pose ta question Tenno." value={q} onChange={e=>setQ(e.target.value)} />
            <ActionButton onClick={ask} disabled={load} icon={load ? Loader2 : Send} className="w-fit px-12">
                {load ? "ANALYSE..." : "TRANSMETTRE"}
            </ActionButton>
        </div>
        {ans && (
            <div className="flex-1 p-12 border border-zinc-900 bg-zinc-950/40 relative">
                <div className="absolute top-0 left-0 w-1 h-12 bg-[#fdc72e]" />
                <p className="text-[9px] font-black text-[#fdc72e] uppercase tracking-[0.5em] mb-6 italic">Archive Reçue</p>
                <div className="text-sm text-zinc-400 leading-relaxed whitespace-pre-wrap font-medium italic">{ans}</div>
            </div>
        )}
      </div>
    </div>
  );
};

const ModerationModule = ({ guild, config, update }) => {
    const [members, setMembers] = useState([]);
    const [search, setSearch] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        setLoading(true);
        fetch(`/api/guilds/${guild.id}/members`).then(r=>r.json()).then(d => {
            setMembers(d || []);
        }).finally(() => setLoading(false));
    }, [guild.id]);

    const handleAction = async (userId, type) => {
        const reason = prompt(`Raison de l'action ${type} :`, "Violation des règles du Nexus.");
        if (!reason) return;
        
        try {
            await fetch(`/api/mod/${type}/${guild.id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ userId, reason })
            });
            alert(`Action ${type} exécutée.`);
        } catch (e) { alert("Erreur de protocole."); }
    };

    const filtered = members.filter(m => m.tag.toLowerCase().includes(search.toLowerCase()));

    return (
        <div className="animate-in fade-in duration-700 text-left">
            <div className="grid md:grid-cols-2 gap-8 mb-12">
                <Card title="Défense Automatisée">
                    <Toggle label="Anti-Liens Discord (Auto)" checked={config.security?.antiLink} onChange={v=>update('security', {...config.security, antiLink:v})} />
                    <Toggle label="Neutralisation Spam" checked={config.security?.antiSpam} onChange={v=>update('security', {...config.security, antiSpam:v})} />
                </Card>
                <div className="flex flex-col justify-end">
                    <Title level={3} className="mb-4">Flux de Surveillance</Title>
                    <div className="relative">
                        <Search size={16} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-700" />
                        <input 
                            placeholder="Rechercher matricule..." 
                            value={search} onChange={e=>setSearch(e.target.value)}
                            className="w-full bg-[#0f0f0f] border border-zinc-900 py-6 pl-16 pr-6 text-white text-sm font-medium outline-none focus:border-[#fdc72e]"
                        />
                    </div>
                </div>
            </div>

            <div className="grid gap-2">
                {loading ? (
                    <div className="p-20 flex flex-col items-center"><Loader2 className="animate-spin text-[#fdc72e]" size={40}/></div>
                ) : filtered.length === 0 ? (
                    <div className="p-20 border border-dashed border-zinc-900 text-center italic text-zinc-800 uppercase text-[10px] tracking-widest font-black">Aucune unité détectée</div>
                ) : filtered.map(m => (
                    <div key={m.id} className="p-8 border border-zinc-900 bg-[#050505] flex flex-col md:flex-row items-start md:items-center justify-between gap-8 group hover:border-zinc-700 transition-all">
                        <div className="flex items-center gap-6">
                            <div className="w-14 h-14 bg-zinc-900 border border-zinc-800 flex items-center justify-center font-black text-xl italic group-hover:bg-[#fdc72e] group-hover:text-black transition-all">
                                {m.tag[0]}
                            </div>
                            <div>
                                <p className="text-xl font-black uppercase italic text-white tracking-tight">{m.tag}</p>
                                <p className="text-[9px] font-mono text-zinc-700 mt-1">{m.id}</p>
                            </div>
                        </div>
                        
                        <div className="flex flex-wrap gap-2">
                            <ActionButton onClick={() => handleAction(m.id, 'mute')} variant="outline" icon={VolumeX}>Sourdine</ActionButton>
                            <ActionButton onClick={() => handleAction(m.id, 'kick')} variant="outline" icon={UserMinus}>Expulser</ActionButton>
                            <ActionButton onClick={() => handleAction(m.id, 'ban')} variant="danger" icon={UserX}>Bannir</ActionButton>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

// --- MODULE OPÉRATIONS PREMIUM ---

const OperationsModule = ({ guild, channels, roles, config, update }) => {
    const [activeEv, setActiveEv] = useState(null);
    const [search, setSearch] = useState("");
    const [members, setMembers] = useState([]);
    const [selectedParticipants, setSelectedParticipants] = useState(new Set());
    const [rolling, setRolling] = useState(false);
    const [winner, setWinner] = useState(null);
    const [newEv, setNewEv] = useState({ 
        title: 'OPÉRATION TITANS PRIME', prize: 'PACK RIVEN ALPHA', 
        desc: 'Transmission orbitale sécurisée.', objectives: 'Liaison au Nexus requise.', 
        img: '', thumbnail: '', footer: 'Protocoles Titans Void', color: '#fdc72e',
        chanId: '', triggerChanId: '', timer: '24', triggerInterval: '60', triggerRoleId: '',
        triggerMessage: '⚠️ Rappel : Liaison orbitale {title} active !'
    });

    const events = config.tirages || [];

    useEffect(() => {
        if (activeEv) {
            fetch(`/api/guilds/${guild.id}/members`).then(r=>r.json()).then(d => {
                setMembers(d || []);
                // On sélectionne tout le monde par défaut au chargement
                setSelectedParticipants(new Set((d || []).map(m => m.id)));
            }).catch(()=>[]);
        }
    }, [activeEv, guild.id]);

    const handleDeploy = async () => {
        if (!newEv.chanId || !newEv.title) return alert("Paramètres incomplets (Salon et Titre).");
        try {
            const evToAdd = { ...newEv, id: Date.now().toString(), date: new Date().toLocaleDateString() };
            const resp = await fetch(`/api/bot/operation/${guild.id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(evToAdd)
            });
            if (resp.ok) {
                update('tirages', [evToAdd, ...events]);
                alert("Opération déployée et archivée.");
            } else { alert("Erreur lors de la transmission orbitale."); }
        } catch (e) { alert("Liaison interrompue."); }
    };

    const toggleMember = (id) => {
        const next = new Set(selectedParticipants);
        if (next.has(id)) next.delete(id); else next.add(id);
        setSelectedParticipants(next);
    };

    const runPick = () => {
        const pool = members.filter(m => selectedParticipants.has(m.id));
        if(!pool.length) return alert("Aucun participant sélectionné !");
        setRolling(true);
        let c = 0;
        const itv = setInterval(() => {
            setWinner(pool[Math.floor(Math.random() * pool.length)]);
            if(++c > 25) { clearInterval(itv); setRolling(false); }
        }, 80);
    };

    if (activeEv) {
        return (
            <div className="animate-in fade-in duration-700 text-left">
                <div className="flex items-center gap-8 mb-16">
                    <button onClick={() => setActiveEv(null)} className="p-4 bg-zinc-900 border border-zinc-800 text-white cursor-pointer hover:bg-zinc-800 transition-all outline-none"><ArrowLeft size={20}/></button>
                    <div><p className="text-[9px] font-black text-[#fdc72e] uppercase tracking-[0.4em] mb-2 italic">Opération Active</p><Title level={2}>{activeEv.title}</Title></div>
                </div>
                <div className="grid lg:grid-cols-12 gap-20">
                    <div className="lg:col-span-8 space-y-12">
                        <div className="bg-zinc-950 border border-zinc-900 p-12 flex flex-col items-center justify-center min-h-[400px] relative overflow-hidden">
                            <Trophy size={100} className="absolute -top-10 -right-10 text-zinc-900 opacity-20" />
                            {winner ? (
                                <div className="text-center animate-in zoom-in duration-300">
                                    <Title level={1} className="text-white mb-6 italic">{winner.tag}</Title>
                                    <p className="bg-[#fdc72e] text-black px-6 py-2 text-[10px] font-black uppercase tracking-widest inline-block italic">Unité Désignée</p>
                                </div>
                            ) : ( <p className="text-zinc-800 font-black uppercase text-xs tracking-[0.5em] italic">Sélectionnez les participants à droite...</p> )}
                        </div>
                        <ActionButton onClick={runPick} disabled={rolling} icon={Zap} className="w-full py-8 text-sm"> {rolling ? "CALCUL..." : "DÉSIGNER GAGNANT"} </ActionButton>
                    </div>
                    <div className="lg:col-span-4 flex flex-col gap-8 h-full">
                        <div className="flex flex-col flex-1 border border-zinc-900 bg-[#0f0f0f] max-h-[600px]">
                            <div className="p-8 border-b border-zinc-900">
                                <Title level={3} className="mb-6">Signaux Détectés ({selectedParticipants.size})</Title>
                                <div className="relative">
                                    <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-700" />
                                    <input placeholder="Filtrer matricule..." value={search} onChange={e=>setSearch(e.target.value)} className="w-full bg-[#0f0f0f] border border-zinc-900 py-4 pl-12 pr-4 text-white text-[10px] font-black uppercase tracking-widest outline-none focus:border-[#fdc72e]" />
                                </div>
                            </div>
                            <div className="flex-1 overflow-y-auto p-4 space-y-2 custom-scrollbar">
                                {members.filter(m => m.tag.toLowerCase().includes(search.toLowerCase())).map(m => (
                                    <div 
                                        key={m.id} 
                                        onClick={() => toggleMember(m.id)}
                                        className={`p-4 border flex justify-between items-center group cursor-pointer transition-all ${selectedParticipants.has(m.id) ? 'bg-[#fdc72e]/10 border-[#fdc72e]' : 'bg-zinc-950/20 border-zinc-900'}`}
                                    >
                                        <span className={`text-[10px] font-black uppercase tracking-tighter ${selectedParticipants.has(m.id) ? 'text-white' : 'text-zinc-600'}`}>{m.tag}</span>
                                        {selectedParticipants.has(m.id) ? <CheckSquare size={14} className="text-[#fdc72e]" /> : <Square size={14} className="text-zinc-800" />}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="grid lg:grid-cols-12 gap-20 animate-in fade-in duration-700 text-left">
            <div className="lg:col-span-7 space-y-12">
                <Card title="Générateur d'Opération Premium">
                    <div className="space-y-10">
                        <section>
                            <Title level={3} className="mb-6 flex items-center gap-4"><Type size={14}/> Liaison Central</Title>
                            <div className="grid md:grid-cols-2 gap-x-10"><Input label="Titre Liaison" value={newEv.title} onChange={e=>setNewEv({...newEv, title:e.target.value})} /><Input label="Lots Prime" value={newEv.prize} onChange={e=>setNewEv({...newEv, prize:e.target.value})} /></div>
                            <Input label="Description Tactique" rows={3} value={newEv.desc} onChange={e=>setNewEv({...newEv, desc:e.target.value})} />
                        </section>
                        <section className="border-t border-zinc-900 pt-10">
                            <Title level={3} className="mb-6 flex items-center gap-4"><Palette size={14}/> Cosmétiques & Assets</Title>
                            <div className="grid md:grid-cols-2 gap-x-10"><Input label="URL Image (Bannière)" placeholder="https://..." value={newEv.img} onChange={e=>setNewEv({...newEv, img:e.target.value})} /><Input label="URL Miniature" placeholder="https://..." value={newEv.thumbnail} onChange={e=>setNewEv({...newEv, thumbnail:e.target.value})} /></div>
                            <div className="grid md:grid-cols-2 gap-x-10"><Input label="Couleur de l'Embed" type="color" value={newEv.color} onChange={e=>setNewEv({...newEv, color:e.target.value})} /><Input label="Texte Pied de Page" value={newEv.footer} onChange={e=>setNewEv({...newEv, footer:e.target.value})} /></div>
                        </section>
                        <section className="border-t border-zinc-900 pt-10">
                            <Title level={3} className="mb-8 flex items-center gap-4"><Repeat size={14}/> Protocole de Rappel & Déploiement</Title>
                            <div className="grid md:grid-cols-2 gap-x-10">
                                <Select label="Salon d'Annonce (Embed)" options={channels.filter(c=>c.type==='text')} value={newEv.chanId} onChange={e=>setNewEv({...newEv, chanId:e.target.value})} />
                                <Select label="Salon des Rappels (Trigger)" options={channels.filter(c=>c.type==='text')} value={newEv.triggerChanId} onChange={e=>setNewEv({...newEv, triggerChanId:e.target.value})} />
                            </div>
                            <div className="grid md:grid-cols-2 gap-x-10">
                                <Input label="Fréquence Rappel (Min)" type="number" value={newEv.triggerInterval} onChange={e=>setNewEv({...newEv, triggerInterval:e.target.value})} />
                                <Select label="Unité de Rappel (Rôle)" options={roles} value={newEv.triggerRoleId} onChange={e=>setNewEv({...newEv, triggerRoleId:e.target.value})} />
                            </div>
                            <Input label="Signal de Rappel" value={newEv.triggerMessage} onChange={e=>setNewEv({...newEv, triggerMessage:e.target.value})} />
                        </section>
                        <ActionButton onClick={handleDeploy} icon={Rocket} className="w-full py-8 mt-4">INITIALISER DÉPLOIEMENT</ActionButton>
                    </div>
                </Card>
                <div className="space-y-6">
                    <Title level={3}>Flux de Prévisualisation</Title>
                    <div style={{ backgroundColor: '#1e1f22' }} className="border border-zinc-900 p-8 max-w-xl">
                        <div style={{ borderLeftColor: newEv.color || '#fdc72e' }} className="border-l-4 bg-[#2b2d31] p-6 relative">
                            {newEv.thumbnail && <img src={newEv.thumbnail} className="absolute top-4 right-4 w-12 h-12 object-cover border border-zinc-700" alt="Thumb"/>}
                            <p className="text-white font-black text-xl italic uppercase mb-2">{newEv.title}</p>
                            <p className="text-zinc-400 text-sm mb-6">{newEv.desc}</p>
                            <div className="grid grid-cols-2 gap-6 text-[10px] uppercase font-black tracking-widest">
                                <div><p className="text-zinc-600 mb-1 flex items-center gap-2"><Trophy size={10}/> Lots</p><p className="text-white italic">{newEv.prize}</p></div>
                                <div><p className="text-zinc-600 mb-1 flex items-center gap-2"><Clock size={10}/> Fin dans</p><p style={{ color: THEME.primary }} className="italic">{newEv.timer}h 00m</p></div>
                            </div>
                            {newEv.img && <img src={newEv.img} alt="Asset" className="w-full h-32 object-cover mt-6 opacity-30 border border-zinc-800" />}
                            <div className="mt-6 pt-4 border-t border-zinc-800 flex justify-between items-center opacity-40"><span className="text-[8px] font-black uppercase text-zinc-500 italic">{newEv.footer}</span><span className="text-[8px] font-black uppercase text-zinc-500 italic">{new Date().toLocaleTimeString()}</span></div>
                        </div>
                    </div>
                </div>
            </div>
            <div className="lg:col-span-5 space-y-12">
                <Title level={3}>Archives Tactiques</Title>
                <div className="space-y-4 max-h-[800px] overflow-y-auto pr-4 custom-scrollbar">
                    {events.length === 0 ? ( <div className="border border-dashed border-zinc-900 p-20 flex flex-col items-center"><History size={32} className="text-zinc-900 mb-4" /><p className="text-zinc-800 font-black uppercase text-[9px] tracking-widest italic text-center">Aucun signal historique</p></div> ) : events.map(ev => (
                        <div key={ev.id} className="p-8 border border-zinc-900 bg-zinc-950/20 group hover:border-[#fdc72e] transition-all"><div className="flex justify-between items-start mb-6"><div><p className="text-[8px] font-black text-zinc-700 uppercase mb-1 tracking-widest">{ev.date}</p><h4 className="text-2xl font-black italic uppercase text-white truncate max-w-[200px]">{ev.title}</h4></div><button onClick={() => update('tirages', events.filter(x=>x.id!==ev.id))} className="text-zinc-800 hover:text-red-500 bg-transparent border-none cursor-pointer"><Trash2 size={16}/></button></div><ActionButton onClick={() => setActiveEv(ev)} variant="outline" className="w-full">RÉCUPÉRER SIGNAL</ActionButton></div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// --- MODULE FORGE EMBEDS PREMIUM ---

const EmbedForge = ({ guild, channels }) => {
    const [e, setE] = useState({ title: 'SIGNAL TITANS', desc: 'Transmission orbitale en cours...', color: '#fdc72e', img: '', thumb: '', footer: 'Secteur Void Protocol' });
    const [targetChan, setTargetChan] = useState('');
    const send = async () => {
        if(!targetChan) return alert("Sélectionnez un salon.");
        try {
            await fetch(`/api/bot/embed/${guild.id}`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ chanId: targetChan, embed: e }) });
            alert("Signal transmis.");
        } catch { alert("Échec de la transmission."); }
    };
    return (
        <div className="grid lg:grid-cols-2 gap-20 animate-in fade-in duration-700 text-left">
            <div className="space-y-4">
                <Card title="Configuration Forge">
                    <Select label="Salon de Déploiement" options={channels.filter(c=>c.type==='text')} value={targetChan} onChange={ev=>setTargetChan(ev.target.value)} />
                    <Input label="Titre" value={e.title} onChange={ev=>setE({...e, title:ev.target.value})} />
                    <Input label="Description" rows={4} value={e.desc} onChange={ev=>setE({...e, desc:ev.target.value})} />
                    <div className="grid grid-cols-2 gap-x-10"><Input label="Couleur" type="color" value={e.color} onChange={ev=>setE({...e, color:ev.target.value})} /><Input label="URL Miniature" value={e.thumb} onChange={ev=>setE({...e, thumb:ev.target.value})} /></div>
                    <Input label="URL Image (Bannière)" value={e.img} onChange={ev=>setE({...e, img:ev.target.value})} />
                    <Input label="Pied de Page" value={e.footer} onChange={ev=>setE({...e, footer:ev.target.value})} />
                    <ActionButton icon={Send} onClick={send} className="w-full py-6 mt-4">DÉPLOYER SIGNAL</ActionButton>
                </Card>
            </div>
            <div>
                <Title level={3} className="mb-8">Aperçu Signal</Title>
                <div style={{ backgroundColor: '#1e1f22' }} className="p-8 border border-zinc-900 h-fit">
                    <div style={{ borderLeftColor: e.color }} className="border-l-4 bg-[#2b2d31] p-6 relative">
                        {e.thumb && <img src={e.thumb} className="absolute top-4 right-4 w-12 h-12 object-cover border border-zinc-700" alt="Thumb"/>}
                        <p className="text-white font-black text-xl italic uppercase mb-2">{e.title}</p>
                        <p className="text-zinc-400 text-sm mb-6 leading-relaxed">{e.desc}</p>
                        {e.img && <img src={e.img} alt="Banner" className="w-full h-32 object-cover mt-6 opacity-30 border border-zinc-800" />}
                        <div className="mt-6 pt-4 border-t border-zinc-800 flex justify-between items-center opacity-40"><span className="text-[8px] font-black uppercase text-zinc-500 italic">{e.footer}</span></div>
                    </div>
                </div>
            </div>
        </div>
    );
};

// --- MODULE REACTION ROLES ---

const ReactionRoleModule = ({ roles, channels, config, update }) => {
    const [msg, setMsg] = useState({ title: 'RÔLES TENNO', desc: 'SÉLECTIONNEZ VOS ACCÈS AU NEYUS.', color: '#fdc72e', channelId: '' });
    const [mappings, setMappings] = useState(config.reactionRoles?.mappings || []);

    const addMapping = () => setMappings([...mappings, { roleId: '', label: '', color: 'gold' }]);
    const removeMapping = (i) => setMappings(mappings.filter((_, idx) => idx !== i));

    const deploy = async () => {
        if(!msg.channelId) return alert("Sélectionnez un salon.");
        const payload = { ...msg, mappings };
        try {
            await fetch(`/api/bot/reaction-role`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            update('reactionRoles', payload);
            alert("Signal Reaction Role déployé.");
        } catch { alert("Erreur de transmission."); }
    };

    return (
        <div className="animate-in fade-in duration-700 text-left">
            <div className="grid lg:grid-cols-2 gap-12">
                <Card title="Forge de Reaction Role">
                    <Select label="Salon d'Ancrage" options={channels.filter(c=>c.type==='text')} value={msg.channelId} onChange={e=>setMsg({...msg, channelId:e.target.value})} />
                    <Input label="Titre de l'Embed" value={msg.title} onChange={e=>setMsg({...msg, title:e.target.value})} />
                    <Input label="Description" rows={3} value={msg.desc} onChange={e=>setMsg({...msg, desc:e.target.value})} />
                    <Input label="Couleur" type="color" value={msg.color} onChange={e=>setMsg({...msg, color:e.target.value})} />
                </Card>

                <div className="space-y-6">
                    <div className="flex justify-between items-center">
                        <Title level={3}>Mappage des Protocoles</Title>
                        <ActionButton onClick={addMapping} icon={Plus} variant="outline" className="py-2">Ajouter</ActionButton>
                    </div>
                    <div className="space-y-4 max-h-[500px] overflow-y-auto pr-4 custom-scrollbar">
                        {mappings.map((m, i) => (
                            <div key={i} className="p-6 bg-zinc-950 border border-zinc-900 flex flex-col gap-4 relative">
                                <button onClick={() => removeMapping(i)} className="absolute top-4 right-4 text-zinc-800 hover:text-red-500 bg-transparent border-none cursor-pointer"><Trash2 size={16}/></button>
                                <Select label="Rôle Unité" options={roles} value={m.roleId} onChange={e=> {
                                    const next = [...mappings]; next[i].roleId = e.target.value; setMappings(next);
                                }} />
                                <Input label="Label Bouton" value={m.label} onChange={e=> {
                                    const next = [...mappings]; next[i].label = e.target.value; setMappings(next);
                                }} />
                            </div>
                        ))}
                    </div>
                    <ActionButton onClick={deploy} icon={Rocket} className="w-full py-6">DÉPLOYER PROTOCOLE</ActionButton>
                </div>
            </div>
        </div>
    );
};

// --- APP PRINCIPALE ---

export default function App() {
  const [user, setUser] = useState(null);
  const [guilds, setGuilds] = useState([]);
  const [curr, setCurr] = useState(null);
  const [view, setView] = useState('landing');
  const [mod, setMod] = useState('overview');
  const [chans, setChans] = useState([]);
  const [roles, setRoles] = useState([]);
  const [conf, setConf] = useState({});
  const [load, setLoad] = useState(false);
  const [save, setSave] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [isNexusOpen, setIsNexusOpen] = useState(false);

  useEffect(() => {
    const initAuth = async () => {
      if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
        await signInWithCustomToken(auth, __initial_auth_token);
      } else {
        await signInAnonymously(auth);
      }
    };
    initAuth();
    const unsub = onAuthStateChanged(auth, u => {
        if(u) {
            fetch('/api/user/guilds').then(r => r.json()).then(d => { 
                if(d.user) { setUser(d.user); setGuilds(d.guilds || []); setView('select'); }
            }).catch(() => setView('landing'));
        }
    });
    return () => unsub();
  }, []);

  const select = async (g) => {
    if(!g.botPresent) return;
    setLoad(true);
    try {
      const [chResp, rolResp, snap] = await Promise.all([
        fetch(`/api/guilds/${g.id}/channels`).then(r=>r.json()).catch(()=>[]),
        fetch(`/api/guilds/${g.id}/roles`).then(r=>r.json()).catch(()=>[]),
        getDoc(doc(db, 'artifacts', appId, 'public', 'data', 'guild_configs', g.id))
      ]);
      setChans(chResp || []); 
      setRoles(rolResp || []);
      setConf(snap.exists() ? snap.data() : {});
      setCurr(g);
      setMod('overview');
      setView('dashboard');
      setIsNexusOpen(false);
    } catch (err) {
      console.error("Erreur de liaison:", err);
    } finally {
      setLoad(false);
    }
  };

  const sync = async () => {
    if(!curr) return;
    setSave(true);
    try {
      await setDoc(doc(db, 'artifacts', appId, 'public', 'data', 'guild_configs', curr.id), conf, {merge:true});
      setHasChanges(false); 
      alert("Nexus synchronisé.");
    } catch (err) {
      console.error("Erreur de sauvegarde:", err);
    } finally { setSave(false); }
  };

  const update = (k, v) => { setConf({...conf, [k]: v}); setHasChanges(true); };

  if (view === 'landing') return (
    <div className="min-h-screen bg-[#0f0f0f] text-white p-24 flex flex-col items-start justify-center text-left">
        <p className="text-[#fdc72e] font-black uppercase tracking-[0.8em] text-[12px] mb-8 italic">Authorization Required</p>
        <Title className="text-[10rem] italic tracking-tighter leading-[0.8] mb-12">TITANS <br/><span className="text-[#fdc72e]">VOID</span></Title>
        <ActionButton onClick={() => window.location.href = '/api/auth/login'} className="px-20 py-8 text-sm">Initialiser Liaison</ActionButton>
    </div>
  );

  if (view === 'select') return (
    <div className="min-h-screen bg-[#0f0f0f] p-24 flex flex-col items-start overflow-y-auto text-left">
        <div className="mb-24">
            <p className="text-[#fdc72e] font-black uppercase tracking-[0.6em] text-[10px] mb-4">Secteurs Détectés</p>
            <Title className="text-9xl italic tracking-tighter">CENTRAL</Title>
        </div>
        <div className="w-full max-w-7xl border border-zinc-900 divide-y divide-zinc-900 bg-[#050505]">
            {guilds.map(g => (
                <div key={g.id} onClick={() => g.botPresent && select(g)} className={`group p-16 flex items-center justify-between transition-all ${g.botPresent ? 'hover:bg-zinc-950 cursor-pointer' : 'opacity-10 grayscale cursor-not-allowed'}`}>
                    <div className="flex items-center gap-12 text-left">
                        <div className="w-20 h-20 bg-zinc-900 border border-zinc-800 flex items-center justify-center font-black text-4xl italic group-hover:bg-[#fdc72e] group-hover:text-black transition-all">
                            {g.icon ? <img src={`https://cdn.discordapp.com/icons/${g.id}/${g.icon}.png`} className="w-full h-full object-cover" /> : g.name[0]}
                        </div>
                        <div>
                            <p className="text-5xl font-black uppercase italic tracking-tighter group-hover:text-[#fdc72e] transition-colors">{g.name}</p>
                            <p className="text-[10px] font-black uppercase tracking-[0.4em] text-zinc-700 mt-4 italic">{g.approximate_member_count || '--'} Tenno Signalés</p>
                        </div>
                    </div>
                    {g.botPresent && <ChevronRight size={48} className="text-zinc-900 group-hover:text-[#fdc72e] transition-colors" />}
                </div>
            ))}
        </div>
    </div>
  );

  if (load) return <div className="min-h-screen bg-[#0f0f0f] flex flex-col items-center justify-center gap-10 text-[#fdc72e]"><Loader2 className="animate-spin" size={64}/><p className="font-black uppercase tracking-[0.5em] text-xs">Synchronisation du Void...</p></div>;

  return (
    <div className="min-h-screen bg-[#0f0f0f] flex text-white font-sans antialiased overflow-hidden">
      <aside className="w-80 border-r border-zinc-900 bg-[#050505] flex flex-col shrink-0 z-50 text-left">
        <div className="p-12 pb-20">
            <div className="text-4xl font-black tracking-tighter italic leading-none">TITANS</div>
            <p className="text-[8px] font-black text-[#fdc72e] uppercase tracking-[0.4em] mt-2">Secteur Void</p>
        </div>
        <nav className="flex-1 px-8 space-y-1">
            <NavBtn id="overview" label="Dashboard" icon={LayoutDashboard} active={mod} set={setMod} />
            <div className="h-px bg-zinc-900 my-10 w-12" />
            <NavBtn id="ai" label="IA Céphalon" icon={Brain} active={mod} set={setMod} />
            <NavBtn id="moderation" label="Modération" icon={Gavel} active={mod} set={setMod} />
            <NavBtn id="voice" label="Logs Vocaux" icon={Mic} active={mod} set={setMod} />
            <NavBtn id="triggers" label="Signaux" icon={Zap} active={mod} set={setMod} />
            <NavBtn id="reaction" label="Reaction Role" icon={MousePointer2} active={mod} set={setMod} />
            <NavBtn id="tirages" label="Opérations" icon={Trophy} active={mod} set={setMod} />
            <NavBtn id="embed" label="Forge Embed" icon={MessageSquare} active={mod} set={setMod} />
            <NavBtn id="security" label="Défense" icon={ShieldAlert} active={mod} set={setMod} />
        </nav>
        <div className="p-12 border-t border-zinc-900">
            <div className="mb-6"><p className="text-[9px] font-black text-zinc-700 uppercase tracking-widest">{user?.username}</p></div>
            <button onClick={() => window.location.reload()} className="flex items-center gap-3 text-zinc-800 hover:text-white transition-all text-[10px] font-black uppercase tracking-[0.4em] bg-transparent border-none cursor-pointer"><LogOut size={16}/> Déconnexion</button>
        </div>
      </aside>

      <main className="flex-1 flex flex-col overflow-hidden relative">
        <header className="h-28 px-16 flex items-center justify-between border-b border-zinc-900 bg-[#050505]/50 backdrop-blur-md">
            <div className="flex items-center gap-10">
                <div className="bg-[#fdc72e] text-black px-5 py-2 font-black text-[10px] uppercase italic tracking-widest">Shard Liaison</div>
                <Title level={2} className="text-2xl">{curr?.name}</Title>
            </div>
            <div className="flex items-center gap-8">
                <ActionButton onClick={sync} disabled={!hasChanges || save} icon={save ? Loader2 : Save}>{save ? "SYNC..." : "SAUVEGARDER"}</ActionButton>
                <button onClick={() => setIsNexusOpen(true)} className="bg-transparent border border-zinc-900 p-5 text-zinc-600 hover:text-[#fdc72e] hover:border-[#fdc72e] cursor-pointer transition-all flex items-center gap-4 outline-none">
                    <Globe size={20}/><span className="text-[9px] font-black uppercase tracking-widest">Nexus</span>
                </button>
            </div>
        </header>

        <div className="flex-1 overflow-y-auto p-20 custom-scrollbar text-left">
            <div className="max-w-7xl">
                <div className="mb-24"><Title level={1} className="mb-4">{mod}</Title><div className="h-1.5 w-24 bg-[#fdc72e]" /></div>
                
                {mod === 'overview' && <Overview guild={curr} channels={chans} />}
                {mod === 'ai' && <AIModule />}
                {mod === 'moderation' && <ModerationModule guild={curr} config={conf} update={update} />}
                
                {mod === 'voice' && (
                  <div className="max-w-2xl animate-in fade-in duration-700">
                    <Select label="Destination des Logs" options={chans.filter(c=>c.type==='text')} value={conf.voiceLogs?.channelId} onChange={e=>update('voiceLogs', {...conf.voiceLogs, channelId:e.target.value})} />
                    <div className="space-y-2 mt-10">
                      <Toggle label="Entrées" checked={conf.voiceLogs?.join} onChange={v=>update('voiceLogs', {...conf.voiceLogs, join:v})} />
                      <Toggle label="Sorties" checked={conf.voiceLogs?.leave} onChange={v=>update('voiceLogs', {...conf.voiceLogs, leave:v})} />
                      <Toggle label="Mouvements (Détaillés)" checked={conf.voiceLogs?.move} onChange={v=>update('voiceLogs', {...conf.voiceLogs, move:v})} />
                    </div>
                  </div>
                )}

                {mod === 'triggers' && (
                  <div className="animate-in fade-in duration-700 space-y-24">
                    <div>
                        <Title level={3} className="mb-8">Signaux Vocaux (Avancés)</Title>
                        <ActionButton onClick={()=>update('triggers', [...(conf.triggers||[]), {id:Date.now(), voiceId:'', channelId:'', message:'', roleId:''}])} icon={Plus} className="mb-10 py-6 w-full max-w-sm">Nouveau Signal Vocal</ActionButton>
                        <div className="grid gap-6">
                        {(conf.triggers||[]).map(t => (
                            <Card key={t.id} className="relative border-l-2 border-l-[#fdc72e]">
                            <button onClick={()=>update('triggers', conf.triggers.filter(x=>x.id!==t.id))} className="absolute top-4 right-4 text-zinc-800 hover:text-red-500 bg-transparent border-none"><Trash2 size={16}/></button>
                            <div className="grid md:grid-cols-2 gap-10">
                                <Select label="Source (Vocal)" options={chans.filter(c=>c.type==='voice')} value={t.voiceId} onChange={e=>update('triggers', conf.triggers.map(x=>x.id===t.id?{...x, voiceId:e.target.value}:x))} />
                                <Select label="Condition Rôle (Seulement si possède)" options={roles} value={t.roleId} onChange={e=>update('triggers', conf.triggers.map(x=>x.id===t.id?{...x, roleId:e.target.value}:x))} />
                                <Select label="Cible (Texte)" options={chans.filter(c=>c.type==='text')} value={t.channelId} onChange={e=>update('triggers', conf.triggers.map(x=>x.id===t.id?{...x, channelId:e.target.value}:x))} />
                            </div>
                            <Input label="Message" value={t.message} onChange={e=>update('triggers', conf.triggers.map(x=>x.id===t.id?{...x, message:e.target.value}:x))} />
                            </Card>
                        ))}
                        </div>
                    </div>

                    <div>
                        <Title level={3} className="mb-8">Signaux d'Obtention de Rôle</Title>
                        <ActionButton onClick={()=>update('roleGrantTriggers', [...(conf.roleGrantTriggers||[]), {id:Date.now(), roleId:'', channelId:'', message:''}])} icon={Plus} className="mb-10 py-6 w-full max-w-sm">Nouveau Signal d'Unité</ActionButton>
                        <div className="grid gap-6">
                        {(conf.roleGrantTriggers||[]).map(t => (
                            <Card key={t.id} className="relative border-l-2 border-l-blue-500">
                            <button onClick={()=>update('roleGrantTriggers', conf.roleGrantTriggers.filter(x=>x.id!==t.id))} className="absolute top-4 right-4 text-zinc-800 hover:text-red-500 bg-transparent border-none"><Trash2 size={16}/></button>
                            <div className="grid md:grid-cols-2 gap-10">
                                <Select label="Rôle Détecté" options={roles} value={t.roleId} onChange={e=>update('roleGrantTriggers', conf.roleGrantTriggers.map(x=>x.id===t.id?{...x, roleId:e.target.value}:x))} />
                                <Select label="Cible (Texte)" options={chans.filter(c=>c.type==='text')} value={t.channelId} onChange={e=>update('roleGrantTriggers', conf.roleGrantTriggers.map(x=>x.id===t.id?{...x, channelId:e.target.value}:x))} />
                            </div>
                            <Input label="Message" value={t.message} onChange={e=>update('roleGrantTriggers', conf.roleGrantTriggers.map(x=>x.id===t.id?{...x, message:e.target.value}:x))} />
                            </Card>
                        ))}
                        </div>
                    </div>
                  </div>
                )}

                {mod === 'reaction' && <ReactionRoleModule roles={roles} channels={chans} config={conf} update={update} />}

                {mod === 'tirages' && <OperationsModule guild={curr} channels={chans} roles={roles} config={conf} update={update} />}
                {mod === 'embed' && <EmbedForge guild={curr} channels={chans} />}

                {mod === 'security' && (
                    <div className="max-w-2xl animate-in fade-in duration-700">
                        <Toggle label="Anti-Liens Discord (Auto)" checked={conf.security?.antiLink} onChange={v=>update('security', {...conf.security, antiLink:v})} />
                        <Toggle label="Neutralisation Spam" checked={conf.security?.antiSpam} onChange={v=>update('security', {...conf.security, antiSpam:v})} />
                    </div>
                )}
            </div>
        </div>

        {/* NEXUS DRAWER (DROITE) */}
        <div className={`fixed inset-0 z-[100] transition-opacity duration-300 ${isNexusOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}>
            <div className="absolute inset-0 bg-black/95 backdrop-blur-md" onClick={() => setIsNexusOpen(false)} />
            <aside className={`absolute right-0 top-0 bottom-0 w-[450px] bg-[#050505] border-l border-zinc-900 p-16 transition-transform duration-500 transform ${isNexusOpen ? 'translate-x-0' : 'translate-x-full'}`}>
                <div className="flex justify-between items-center mb-20">
                    <div className="text-left">
                      <Title level={3} className="text-2xl italic tracking-tighter">Secteurs Connus</Title>
                      <div className="h-1 w-12 bg-[#fdc72e] mt-2"></div>
                    </div>
                    <button onClick={() => setIsNexusOpen(false)} className="text-zinc-700 hover:text-white bg-transparent border-none cursor-pointer transition-colors outline-none"><X size={32}/></button>
                </div>
                
                <div className="space-y-4 overflow-y-auto max-h-[calc(100vh-350px)] pr-6 custom-scrollbar">
                    {guilds.map(g => (
                        <div 
                          key={g.id} 
                          onClick={() => g.botPresent && select(g)}
                          className={`group p-8 rounded-none border transition-all cursor-pointer flex items-center gap-8 ${
                            curr?.id === g.id ? 'bg-[#fdc72e] border-none' : 'bg-black border-zinc-900 hover:border-zinc-700'
                          } ${!g.botPresent && 'opacity-10 grayscale cursor-not-allowed'}`}
                        >
                            <div className={`w-14 h-14 rounded-none flex items-center justify-center font-black text-xl border ${curr?.id === g.id ? 'bg-black text-white border-black' : 'bg-zinc-950 text-zinc-800 border-zinc-900'}`}>
                                {g.icon ? <img src={`https://cdn.discordapp.com/icons/${g.id}/${g.icon}.png`} className="w-full h-full object-cover" /> : g.name[0]}
                            </div>
                            <div className="text-left flex-1 min-w-0">
                                <p className={`text-base font-black uppercase truncate italic ${curr?.id === g.id ? 'text-black' : 'text-white'}`}>{g.name}</p>
                                <p className={`text-[9px] font-bold uppercase tracking-[0.2em] mt-2 ${curr?.id === g.id ? 'text-black/60' : 'text-zinc-700'}`}>
                                    {g.botPresent ? "Liaison Établie" : "Signal Perdu"}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </aside>
        </div>
      </main>
    </div>
  );
}

const NavBtn = ({ id, label, icon: Icon, active, set }) => (
    <button onClick={() => set(id)} className={`flex items-center gap-6 px-6 py-5 rounded-none transition-all font-black group bg-transparent border-none cursor-pointer w-full text-left relative ${active === id ? 'text-[#fdc72e] translate-x-2' : 'text-[#ffffff] hover:text-[#fdc72e]'}`}>
        <Icon size={18} className="text-[#fdc72e]" />
        <span className="text-[11px] uppercase tracking-[0.2em] italic">{label}</span>
    </button>
);
""".replace("___API_KEY___", fb_api_key).replace("___PROJECT_ID___.firebaseapp.com", f"{fb_project_id}.firebaseapp.com").replace("___PROJECT_ID___", fb_project_id).replace("___SENDER_ID___", fb_sender_id).replace("___APP_ID___", fb_app_id).replace("___CLIENT_ID___", discord_client_id)

# ==========================================
# 3. CODE DU SERVEUR (API)
# ==========================================
server_index_js = """require('dotenv').config();
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
"""

# ==========================================
# 4. CODE DU BOT (CORE - RÉPARÉ & LOGS PIMPÉS & TRIGGERS AVANCÉS)
# ==========================================
bot_index_js = """require('dotenv').config();
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
            embed.setColor('#2ecc71').setTitle('📥 ENTRÉE DÉTECTÉE').setDescription(`**Tenno :** <@${newState.member.id}>\\n**Salon :** \`${newState.channel.name}\``);
            logChan.send({ embeds: [embed] });
        } 
        // LEAVE
        else if (oldState.channelId && !newState.channelId && config.voiceLogs.leave) {
            embed.setColor('#e74c3c').setTitle('📤 SORTIE DÉTECTÉE').setDescription(`**Tenno :** <@${oldState.member.id}>\\n**Salon quitté :** \`${oldState.channel.name}\``);
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
            let desc = `**Tenno :** <@${newState.member.id}>\\n**Ancien :** \`${oldState.channel.name}\`\\n**Nouveau :** \`${newState.channel.name}\``;
            
            if (mover) {
                desc += `\\n**Déplacé par :** <@${mover.id}>`;
            } else {
                desc += `\\n**Note :** Le membre s'est déplacé de lui-même.`;
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
    if (config?.security?.antiLink && /https?:\/\/[^\\s]+/.test(message.content)) {
        await message.delete().catch(() => {});
        const m = await message.channel.send(`🚫 **${message.author.username}**, liens interdits.`);
        setTimeout(() => m.delete(), 3000);
    }
});

client.login(process.env.BOT_TOKEN);
"""

# ==========================================
# 5. ÉCRITURE DES FICHIERS
# ==========================================
def write_file(path, content):
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Fichier mis à jour : {path}")

write_file(f"{dashboard_dir}/client/src/App.jsx", client_app_jsx)
write_file(f"{dashboard_dir}/server/index.js", server_index_js)
write_file(f"{bot_dir}/index.js", bot_index_js)
write_file("start_dev.bat", bat_content)

print("\n✨ MODULES MIS À JOUR : Logs de déplacement audités, Triggers avec Rôles, Reaction Roles & Sync des tirages opérationnels !")