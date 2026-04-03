/**
 * Fetch all WFRP 1e career advance schemes from Wayback archive using Playwright.
 * Run with: node _fetch_schemes.js
 */
const { chromium } = require('playwright');
const fs = require('fs');

const BASE = "https://web.archive.org/web/20250123094744/https://wfrp1e.fandom.com/wiki/";
const STAT_KEYS = ["M","WS","BS","S","T","W","I","A","Dex","Ld","Int","Cl","WP","Fel"];

const CAREERS = [
  ["Bodyguard","Bodyguard"],["Labourer","Labourer"],["Marine","Marine"],
  ["Mercenary","Mercenary"],["Militiaman","Militiaman"],["Noble","Noble"],
  ["Outlaw","Outlaw"],["Pit_Fighter","Pit Fighter"],["Protagonist","Protagonist"],
  ["Seaman","Seaman"],["Servant","Servant"],["Soldier","Soldier"],["Squire","Squire"],
  ["Troll_Slayer","Troll Slayer"],["Tunnel_Fighter","Tunnel Fighter"],["Watchman","Watchman"],
  ["Boatman","Boatman"],["Bounty_Hunter","Bounty Hunter"],["Coachman","Coachman"],
  ["Farmer","Farmer"],["Fisherman","Fisherman"],["Gamekeeper","Gamekeeper"],
  ["Herdsman","Herdsman"],["Hunter","Hunter"],["Miner","Miner"],
  ["Muleskinner","Muleskinner"],["Outrider","Outrider"],["Pilot","Pilot"],
  ["Prospector","Prospector"],["Rat_Catcher","Rat Catcher"],["Roadwarden","Roadwarden"],
  ["Runner","Runner"],["Toll-Keeper","Toll-Keeper"],["Trapper","Trapper"],["Woodsman","Woodsman"],
  ["Agitator","Agitator"],["Bawd","Bawd"],["Beggar","Beggar"],
  ["Entertainer","Entertainer"],["Footpad","Footpad"],["Gambler","Gambler"],
  ["Grave_Robber","Grave Robber"],["Jailer","Jailer"],["Minstrel","Minstrel"],
  ["Pedlar","Pedlar"],["Raconteur","Raconteur"],["Rustler","Rustler"],
  ["Smuggler","Smuggler"],["Thief","Thief"],["Tomb_Robber","Tomb Robber"],
  ["Alchemist%27s_Apprentice","Alchemist's Apprentice"],
  ["Artisan%27s_Apprentice","Artisan's Apprentice"],
  ["Druid","Druid"],["Engineer","Engineer"],["Exciseman","Exciseman"],
  ["Herbalist","Herbalist"],["Hedge-Wizard%27s_Apprentice","Hedge-Wizard's Apprentice"],
  ["Hypnotist","Hypnotist"],["Initiate","Initiate"],["Pharmacist","Pharmacist"],
  ["Physician%27s_Student","Physician's Student"],["Runescribe","Runescribe"],
  ["Runesmith%27s_Apprentice","Runesmith's Apprentice"],
  ["Scholar","Scholar"],["Scribe","Scribe"],["Seer","Seer"],["Student","Student"],
  ["Trader","Trader"],["Wizard%27s_Apprentice","Wizard's Apprentice"],
  ["Wood_Elf_Mage%27s_Apprentice","Wood Elf Mage's Apprentice"],
];

function parseCells(cells) {
  const scheme = {};
  for (let i = 0; i < STAT_KEYS.length && i < cells.length; i++) {
    const v = cells[i].replace('+','').replace('\u00a0','').trim();
    if (v && v !== '' && v !== '-') {
      const n = parseInt(v);
      if (!isNaN(n) && n !== 0) scheme[STAT_KEYS[i]] = n;
    }
  }
  return scheme;
}

async function getScheme(page, slug, display) {
  const url = BASE + slug;
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    // Wait for the advance scheme table
    await page.waitForSelector('table', { timeout: 10000 }).catch(() => {});
    const cells = await page.evaluate(() => {
      const tbls = document.querySelectorAll('table');
      for (const tbl of tbls) {
        const rows = tbl.querySelectorAll('tr');
        for (const row of rows) {
          const tds = row.querySelectorAll('td');
          if (tds.length >= 14) {
            return Array.from(tds).map(td => td.innerText.trim());
          }
        }
      }
      return null;
    });
    if (!cells) { console.log(`  ${display}: (no table data)`); return {}; }
    const scheme = parseCells(cells);
    const nonZero = Object.entries(scheme).filter(([,v]) => v).map(([k,v]) => `${k}:${v}`).join(' ');
    console.log(`  ${display}: ${nonZero || '(empty)'}`);
    return scheme;
  } catch (e) {
    console.log(`  ${display}: ERROR ${e.message.split('\n')[0]}`);
    return {};
  }
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.setExtraHTTPHeaders({ 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0' });

  const results = {};
  for (const [slug, display] of CAREERS) {
    results[display] = await getScheme(page, slug, display);
    await new Promise(r => setTimeout(r, 400));
  }

  await browser.close();

  fs.writeFileSync('_advance_schemes.json', JSON.stringify(results, null, 2));
  const nonEmpty = Object.values(results).filter(v => Object.keys(v).length > 0).length;
  console.log(`\nDone! ${nonEmpty}/${CAREERS.length} careers have schemes → _advance_schemes.json`);
})();
