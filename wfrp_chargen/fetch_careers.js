const https = require('https');
const cheerio = require('cheerio');

const BASE_URL = 'https://web.archive.org/web/20250123094744/https://wfrp1e.fandom.com/wiki/';
const STATS = ['M', 'WS', 'BS', 'S', 'T', 'W', 'I', 'A', 'Dex', 'Ld', 'Int', 'Cl', 'WP', 'Fel'];

const CAREERS = [
  'Soldier', 'Militiaman', 'Thief', 'Hunter', 'Woodsman',
  "Wizard%27s_Apprentice", 'Initiate', 'Scholar', 'Scribe', 'Entertainer',
  'Footpad', 'Pit_Fighter', 'Protagonist', 'Outlaw', 'Roadwarden',
  'Labourer', 'Marine', 'Noble', 'Seaman', 'Servant',
  'Squire', 'Troll_Slayer', 'Tunnel_Fighter', 'Watchman', 'Boatman',
  'Bounty_Hunter', 'Coachman', 'Farmer', 'Fisherman', 'Gamekeeper',
  'Herdsman', 'Miner', 'Muleskinner', 'Outrider', 'Pilot',
  'Prospector', 'Rat_Catcher', 'Runner', 'Toll-Keeper', 'Trapper',
  'Agitator', 'Bawd', 'Beggar', 'Gambler', 'Grave_Robber',
  'Jailer', 'Minstrel', 'Pedlar', 'Raconteur', 'Rustler',
  'Smuggler', 'Tomb_Robber', "Alchemist%27s_Apprentice", "Artisan%27s_Apprentice",
  'Druid', 'Engineer', 'Exciseman', 'Herbalist', "Hedge-Wizard%27s_Apprentice",
  'Hypnotist', 'Pharmacist', "Physician%27s_Student", 'Runescribe',
  "Runesmith%27s_Apprentice", 'Seer', 'Student', 'Trader', "Wood_Elf_Mage%27s_Apprentice"
];

function fetchPage(url) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      timeout: 15000
    }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        fetchPage(res.headers.location).then(resolve).catch(reject);
        return;
      }
      if (res.statusCode === 404) {
        resolve(null);
        return;
      }
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
      res.on('error', reject);
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
  });
}

function parseAdvanceScheme(html) {
  const $ = cheerio.load(html);
  
  // Find the table that contains "Advance Scheme"
  let advanceTable = null;
  
  $('table').each((i, table) => {
    const text = $(table).text();
    if (text.includes('Advance Scheme') || text.includes('M') && text.includes('WS') && text.includes('BS')) {
      const rows = $(table).find('tr');
      if (rows.length >= 2) {
        // Check if first/header row has stat names
        const firstRow = $(rows[0]).find('td, th').map((i, el) => $(el).text().trim()).get();
        const secondRow = $(rows[1]).find('td, th').map((i, el) => $(el).text().trim()).get();
        
        if (firstRow.join('').includes('WS') || secondRow.join('').includes('WS')) {
          advanceTable = table;
          return false; // break
        }
      }
    }
  });
  
  if (!advanceTable) {
    // Try looking for "Advance Scheme" section and find the next table
    let found = false;
    $('p, h2, h3, b, strong, th').each((i, el) => {
      if ($(el).text().trim() === 'Advance Scheme') {
        found = true;
      }
    });
    
    // Look for table containing stat headers
    $('tr').each((i, row) => {
      const cells = $(row).find('td, th').map((i, el) => $(el).text().trim()).get();
      if (cells.includes('M') && cells.includes('WS') && cells.includes('BS') && cells.includes('Fel')) {
        // This is the header row, the next row should have the values
        advanceTable = $(row).closest('table')[0];
        return false;
      }
    });
  }
  
  if (!advanceTable) return null;
  
  const rows = $(advanceTable).find('tr').toArray();
  
  // Find header row and value row
  let headerRow = null;
  let valueRow = null;
  
  for (let i = 0; i < rows.length; i++) {
    const cells = $(rows[i]).find('td, th').map((j, el) => $(el).text().trim()).get();
    if (cells.includes('M') && cells.includes('WS') && cells.includes('Fel')) {
      headerRow = cells;
      if (i + 1 < rows.length) {
        valueRow = $(rows[i + 1]).find('td, th').map((j, el) => $(el).text().trim()).get();
      }
      break;
    }
  }
  
  if (!headerRow || !valueRow) return null;
  
  const result = {};
  STATS.forEach(s => result[s] = 0);
  
  headerRow.forEach((stat, idx) => {
    if (STATS.includes(stat) && idx < valueRow.length) {
      const val = valueRow[idx].trim();
      // Parse: "—", "-", "", blank = 0; "+10" = 10; "+1" = 1; "+20" = 20; "+30" = 30
      if (!val || val === '—' || val === '-' || val === '–') {
        result[stat] = 0;
      } else {
        const num = parseInt(val.replace('+', ''), 10);
        result[stat] = isNaN(num) ? 0 : num;
      }
    }
  });
  
  return result;
}

function getDisplayName(career) {
  return decodeURIComponent(career.replace(/_/g, ' '));
}

async function fetchCareer(career) {
  const url = BASE_URL + career;
  try {
    const html = await fetchPage(url);
    if (!html) {
      return { career: getDisplayName(career), error: '404' };
    }
    const scheme = parseAdvanceScheme(html);
    if (!scheme) {
      return { career: getDisplayName(career), error: 'parse_failed', html_snippet: html.slice(0, 200) };
    }
    return { career: getDisplayName(career), scheme };
  } catch (e) {
    return { career: getDisplayName(career), error: e.message };
  }
}

async function fetchBatch(careers, batchSize = 5) {
  const results = [];
  for (let i = 0; i < careers.length; i += batchSize) {
    const batch = careers.slice(i, i + batchSize);
    process.stderr.write(`Fetching batch ${Math.floor(i/batchSize)+1}: ${batch.map(getDisplayName).join(', ')}\n`);
    const batchResults = await Promise.all(batch.map(fetchCareer));
    results.push(...batchResults);
    // Small delay between batches
    if (i + batchSize < careers.length) {
      await new Promise(r => setTimeout(r, 1000));
    }
  }
  return results;
}

async function main() {
  const results = await fetchBatch(CAREERS, 5);
  
  const schemes = {};
  const errors = [];
  
  results.forEach(r => {
    if (r.scheme) {
      schemes[r.career] = r.scheme;
    } else {
      errors.push(r);
    }
  });
  
  process.stderr.write('\n=== ERRORS ===\n');
  errors.forEach(e => process.stderr.write(`${e.career}: ${e.error}\n`));
  
  process.stderr.write('\n=== RESULTS ===\n');
  console.log(JSON.stringify(schemes, null, 2));
}

main().catch(console.error);
