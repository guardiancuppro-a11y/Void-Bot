const { initializeApp } = require('firebase/app');
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
