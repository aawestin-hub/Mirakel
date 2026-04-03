const officegen = require('officegen');
const fs = require('fs');

const pptx = officegen('pptx');

pptx.on('finalize', function(written) {
  console.log('Done! ' + written + ' bytes written.');
});
pptx.on('error', function(err) {
  console.error('Error:', err);
});

// Fargepalett
const darkGreen = '1a4731';
const midGreen = '2e7d52';
const lightGreen = 'd6ede0';
const white = 'ffffff';
const darkText = '1a2b1f';
const accentGold = 'f0a500';

// Slide 1: Tittelslide
let slide1 = pptx.makeNewSlide();
slide1.back = midGreen;
slide1.addText('HP Link', {
  x: 0.5, y: 1.2, cx: '90%',
  font_size: 54, bold: true, color: white,
  font_face: 'Calibri'
});
slide1.addText('Rekvireringsløsning for elektronisk samhandling', {
  x: 0.5, y: 2.5, cx: '90%',
  font_size: 24, color: 'c8e6d5',
  font_face: 'Calibri'
});
slide1.addText('Samhandlingskonferansen 2026', {
  x: 0.5, y: 4.2, cx: '90%',
  font_size: 18, color: 'c8e6d5', italic: true,
  font_face: 'Calibri'
});
slide1.addText('Helseplattformen AS & Sykehuslaboratoriene i Midt-Norge', {
  x: 0.5, y: 4.8, cx: '90%',
  font_size: 14, color: 'a0c8b0',
  font_face: 'Calibri'
});

// Slide 2: Hva er HP Link?
let slide2 = pptx.makeNewSlide();
slide2.back = white;
slide2.addText('Hva er HP Link?', {
  x: 0.5, y: 0.3, cx: '90%',
  font_size: 36, bold: true, color: darkGreen,
  font_face: 'Calibri'
});
slide2.addText('HP Link er en webløsning for elektronisk samhandling mellom sykehuslaboratoriene i Midt-Norge og aktører på utsiden av Helseplattformen.', {
  x: 0.5, y: 1.3, cx: '90%',
  font_size: 20, color: darkText,
  font_face: 'Calibri'
});
slide2.addText('🔗  En bro mellom to verdener', {
  x: 0.5, y: 2.5, cx: '90%',
  font_size: 22, bold: true, color: midGreen,
  font_face: 'Calibri'
});
slide2.addText('Helseplattformen\n(sykehusenes journalsystem)', {
  x: 0.3, y: 3.2, cx: '40%',
  font_size: 16, color: white, bold: true,
  back: midGreen, align: 'c',
  font_face: 'Calibri'
});
slide2.addText('⟺  HP Link  ⟺', {
  x: 3.8, y: 3.4, cx: '25%',
  font_size: 18, bold: true, color: accentGold,
  font_face: 'Calibri'
});
slide2.addText('EPJ-systemer\npå legekontor m.m.', {
  x: 6.0, y: 3.2, cx: '40%',
  font_size: 16, color: white, bold: true,
  back: midGreen, align: 'c',
  font_face: 'Calibri'
});
slide2.addText('Levert av Helseplattformen AS i samarbeid med sykehuslaboratoriene', {
  x: 0.5, y: 4.8, cx: '90%',
  font_size: 13, italic: true, color: '888888',
  font_face: 'Calibri'
});

// Slide 3: Hvem bruker HP Link?
let slide3 = pptx.makeNewSlide();
slide3.back = white;
slide3.addText('Hvem bruker HP Link?', {
  x: 0.5, y: 0.3, cx: '90%',
  font_size: 36, bold: true, color: darkGreen,
  font_face: 'Calibri'
});
const users = [
  '🏥  Legekontor (fastleger og allmennpraktikere)',
  '👨‍⚕️  Avtalespesialister',
  '🤰  Jordmødre',
  '🏙️  Kommunale helsestasjoner (under utrulling)'
];
let y3 = 1.4;
for (const u of users) {
  slide3.addText(u, {
    x: 0.7, y: y3, cx: '85%',
    font_size: 22, color: darkText,
    font_face: 'Calibri'
  });
  y3 += 0.8;
}
slide3.addText('📊  Nesten alle legekontor i Midt-Norge bruker løsningen!', {
  x: 0.5, y: 4.5, cx: '90%',
  font_size: 20, bold: true, color: midGreen,
  back: lightGreen,
  font_face: 'Calibri'
});

// Slide 4: Hva kan du gjøre?
let slide4 = pptx.makeNewSlide();
slide4.back = white;
slide4.addText('Hva kan du gjøre i HP Link?', {
  x: 0.5, y: 0.3, cx: '90%',
  font_size: 36, bold: true, color: darkGreen,
  font_face: 'Calibri'
});
const features = [
  ['🧪  Rekvirere laboratorieundersøkelser', 'Til alle sykehuslaboratorier i Midt-Norge fra ett og samme sted'],
  ['🔄  Samhandle om prøvetaking', 'Rekvirere ett sted og ta prøver et annet sted – mellom sykehus og legekontor, eller mellom legekontor'],
  ['📋  Innsyn i prøvesvarshistorikk', 'Lab- og bildesvar fra sykehus – opp til 30 år tilbake i tid']
];
let y4 = 1.3;
for (const [title, desc] of features) {
  slide4.addText(title, {
    x: 0.5, y: y4, cx: '90%',
    font_size: 20, bold: true, color: midGreen,
    font_face: 'Calibri'
  });
  slide4.addText(desc, {
    x: 0.9, y: y4 + 0.42, cx: '85%',
    font_size: 16, color: darkText,
    font_face: 'Calibri'
  });
  y4 += 1.1;
}

// Slide 5: Felles analysekatalog
let slide5 = pptx.makeNewSlide();
slide5.back = white;
slide5.addText('Felles analysekatalog for hele regionen', {
  x: 0.5, y: 0.3, cx: '90%',
  font_size: 34, bold: true, color: darkGreen,
  font_face: 'Calibri'
});
slide5.addText('Ved rekvirering i HP Link får man opp én felles analysekatalog for hele Midt-Norge.', {
  x: 0.5, y: 1.3, cx: '90%',
  font_size: 20, color: darkText,
  font_face: 'Calibri'
});
slide5.addText('✅  Du trenger ikke å vite hvilke analyser som gjøres hvor', {
  x: 0.7, y: 2.3, cx: '85%',
  font_size: 18, color: darkText, font_face: 'Calibri'
});
slide5.addText('✅  Laboratoriene sørger selv for eventuell videresending', {
  x: 0.7, y: 2.9, cx: '85%',
  font_size: 18, color: darkText, font_face: 'Calibri'
});
slide5.addText('✅  Tusenvis av laboratorieanalyser tilgjengelig', {
  x: 0.7, y: 3.5, cx: '85%',
  font_size: 18, color: darkText, font_face: 'Calibri'
});
slide5.addText('✅  Brukerhåndbøker for alle laboratoriene tilgjengelig i løsningen', {
  x: 0.7, y: 4.1, cx: '85%',
  font_size: 18, color: darkText, font_face: 'Calibri'
});

// Slide 6: Gratis og enkelt
let slide6 = pptx.makeNewSlide();
slide6.back = midGreen;
slide6.addText('Helt gratis – ingen skjulte kostnader', {
  x: 0.5, y: 0.4, cx: '90%',
  font_size: 34, bold: true, color: white,
  font_face: 'Calibri'
});
const freeItems = [
  '💻  Oppsett og bruk av HP Link er gratis',
  '🖨️  Etikettskrivere inkludert',
  '📚  Opplæring inkludert',
  '🔓  Ingen løpende kostnader',
  '🔗  Ingen bindingstid'
];
let y6 = 1.4;
for (const item of freeItems) {
  slide6.addText(item, {
    x: 0.7, y: y6, cx: '85%',
    font_size: 20, color: white,
    font_face: 'Calibri'
  });
  y6 += 0.65;
}

// Slide 7: Utbredelse og statistikk
let slide7 = pptx.makeNewSlide();
slide7.back = white;
slide7.addText('Utbredelse og status', {
  x: 0.5, y: 0.3, cx: '90%',
  font_size: 36, bold: true, color: darkGreen,
  font_face: 'Calibri'
});
const stats = [
  ['Nesten alle legekontor i Midt-Norge', 'har tatt løsningen i bruk'],
  ['Flere tusen rekvisisjoner', 'legges inn i HP Link daglig'],
  ['Tre fylker dekket', 'Møre og Romsdal, Trøndelag og Nordmøre']
];
let y7 = 1.3;
for (const [big, small] of stats) {
  slide7.addText(big, {
    x: 0.5, y: y7, cx: '90%',
    font_size: 22, bold: true, color: midGreen,
    font_face: 'Calibri'
  });
  slide7.addText(small, {
    x: 0.9, y: y7 + 0.45, cx: '85%',
    font_size: 16, color: darkText,
    font_face: 'Calibri'
  });
  y7 += 1.0;
}

// Slide 8: Veien videre
let slide8 = pptx.makeNewSlide();
slide8.back = white;
slide8.addText('Veien videre', {
  x: 0.5, y: 0.3, cx: '90%',
  font_size: 36, bold: true, color: darkGreen,
  font_face: 'Calibri'
});
const roadmap = [
  ['🩺  Avtalespesialister', 'Jobbes aktivt med tilkobling'],
  ['🏥  Kommunale helsestasjoner', 'Under utrulling'],
  ['🔬  Sykehuslaboratorier i hele Midt-Norge', 'Alle inkludert i felleskatalogen']
];
let y8 = 1.3;
for (const [title, status] of roadmap) {
  slide8.addText(title, {
    x: 0.5, y: y8, cx: '60%',
    font_size: 20, bold: true, color: darkText,
    font_face: 'Calibri'
  });
  slide8.addText('→ ' + status, {
    x: 6.0, y: y8, cx: '35%',
    font_size: 16, italic: true, color: midGreen,
    font_face: 'Calibri'
  });
  y8 += 0.9;
}
slide8.addText('"24 gode grunner til å bruke sykehuslaboratoriet"\nVideoserie med overlege Andreas Austgulen Westin, St. Olavs hospital', {
  x: 0.5, y: 4.0, cx: '90%',
  font_size: 15, italic: true, color: '666666',
  back: 'f5f5f5',
  font_face: 'Calibri'
});

// Slide 9: Kom i gang
let slide9 = pptx.makeNewSlide();
slide9.back = white;
slide9.addText('Kom i gang med HP Link', {
  x: 0.5, y: 0.3, cx: '90%',
  font_size: 36, bold: true, color: darkGreen,
  font_face: 'Calibri'
});
const steps = [
  '1️⃣  Gå til www.helse-midt.no/HPLink',
  '2️⃣  Klikk "Bestill tilgang"',
  '3️⃣  Motta etikettskriver og opplæring',
  '4️⃣  Start å rekvirere elektronisk!'
];
let y9 = 1.3;
for (const step of steps) {
  slide9.addText(step, {
    x: 0.7, y: y9, cx: '85%',
    font_size: 21, color: darkText,
    font_face: 'Calibri'
  });
  y9 += 0.8;
}
slide9.addText('📞  481 57 680     ✉️  post.hplink@helse-midt.no', {
  x: 0.5, y: 4.5, cx: '90%',
  font_size: 18, bold: true, color: white,
  back: midGreen,
  font_face: 'Calibri'
});

// Slide 10: Avslutning
let slide10 = pptx.makeNewSlide();
slide10.back = darkGreen;
slide10.addText('HP Link', {
  x: 0.5, y: 1.0, cx: '90%',
  font_size: 52, bold: true, color: white,
  align: 'c', font_face: 'Calibri'
});
slide10.addText('Enklere samhandling.\nBedre pasientbehandling.', {
  x: 0.5, y: 2.5, cx: '90%',
  font_size: 26, color: 'c8e6d5',
  align: 'c', font_face: 'Calibri'
});
slide10.addText('www.helse-midt.no/HPLink', {
  x: 0.5, y: 4.2, cx: '90%',
  font_size: 18, color: 'a0c8b0',
  align: 'c', font_face: 'Calibri'
});

// Write file
const out = fs.createWriteStream('HP-Link-Presentasjon.pptx');
out.on('error', function(err) { console.error('Write error:', err); });
pptx.generate(out);
