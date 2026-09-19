const element = id => document.getElementById(id);
const node = (tag, text, className) => {
  const result = document.createElement(tag);
  if (text !== undefined) result.textContent = text;
  if (className) result.className = className;
  return result;
};
const numberFormat = new Intl.NumberFormat('en', {maximumFractionDigits: 2});
const money = (amount, currency) => amount === null ? 'Unknown' : currency + ' ' + numberFormat.format(amount);
const uniqueValues = (rows, key) => [...new Set(rows.map(row => row[key]))].sort();
let pageIndex = 0;
let matchingCases = [];
const pageSize = 25;
for (const key of ['category', 'channel', 'currency']) {
  const select = element(key + '-filter');
  select.append(new Option('All', ''));
  for (const value of uniqueValues(SNAPSHOT.records, key)) select.append(new Option(value, value));
  select.addEventListener('change', renderAll);
}
function filteredRecords() {
  return SNAPSHOT.records.filter(row => ['category', 'channel', 'currency'].every(key => !element(key + '-filter').value || row[key] === element(key + '-filter').value));
}
function amountGroups(rows) {
  const groups = new Map();
  for (const row of rows) {
    if (!groups.has(row.currency)) groups.set(row.currency, {sum: 0, known: 0, unknown: 0});
    const group = groups.get(row.currency);
    if (row.amount === null) group.unknown++;
    else {group.sum += row.amount; group.known++;}
  }
  return groups;
}
function renderOverview(rows) {
  const flagged = rows.filter(row => row.prediction.is_fraud);
  const cards = element('overview-cards');
  cards.replaceChildren();
  for (const [label, value, note] of [
    ['Unique transactions', rows.length, 'Filtered from ' + SNAPSHOT.records.length + ' unique / ' + SNAPSHOT.source_rows + ' source rows'],
    ['Model flagged', flagged.length, 'Not confirmed fraud'],
    ['Flagged rate', rows.length ? (100 * flagged.length / rows.length).toFixed(1) + '%' : '—', 'Denominator: filtered unique transactions'],
    ['With quality warnings', rows.filter(row => row.quality_flags.length).length, 'Unknown features or relationship flags'],
  ]) {
    const card = node('div', undefined, 'card');
    card.append(node('span', label), node('span', value, 'value'), node('small', note));
    cards.append(card);
  }
  const amounts = [...amountGroups(flagged)].map(([currency, value]) => money(value.sum, currency) + ' (' + value.known + ' known amounts; ' + value.unknown + ' unknown)');
  element('amount-summary').textContent = 'Flagged transaction amounts—not confirmed loss: ' + (amounts.join(' · ') || 'No flagged cases in this selection.');
}
function renderHeatmap(rows) {
  const channels = uniqueValues(rows, 'channel');
  const categories = uniqueValues(rows, 'category');
  const header = node('tr');
  header.append(node('th', 'Category'));
  channels.forEach(channel => header.append(node('th', channel)));
  element('heatmap-table').querySelector('thead').replaceChildren(header);
  const body = element('heatmap-table').querySelector('tbody');
  body.replaceChildren();
  for (const category of categories) {
    const rowNode = node('tr');
    rowNode.append(node('th', category));
    for (const channel of channels) {
      const cases = rows.filter(row => row.category === category && row.channel === channel);
      const cell = node('td');
      if (!cases.length) cell.textContent = '—';
      else {
        const flagged = cases.filter(row => row.prediction.is_fraud).length;
        const rate = flagged / cases.length;
        const button = node('button', flagged + '/' + cases.length + ' · ' + (rate * 100).toFixed(1) + '%');
        button.type = 'button';
        button.style.backgroundColor = 'hsl(174 40% ' + (96 - rate * 35) + '%)';
        button.style.color = '#12352e';
        button.setAttribute('aria-label', category + ', ' + channel + ': ' + flagged + ' flagged of ' + cases.length + '; filter cases');
        button.addEventListener('click', () => {
          element('category-filter').value = category;
          element('channel-filter').value = channel;
          renderAll();
          element('queue').scrollIntoView({block: 'start'});
        });
        cell.append(button);
        if (cases.length < 20) cell.append(node('div', 'Low sample (<20)', 'muted'));
      }
      rowNode.append(cell);
    }
    body.append(rowNode);
  }
  if (!rows.length) {
    const row = node('tr');
    row.append(node('td', 'No transactions match these filters.'));
    body.append(row);
  }
  const amounts = element('sector-amounts').querySelector('tbody');
  amounts.replaceChildren();
  for (const category of categories) {
    const flagged = rows.filter(row => row.category === category && row.prediction.is_fraud);
    for (const [currency, group] of amountGroups(flagged)) {
      const row = node('tr');
      [category, currency, numberFormat.format(group.sum), group.known, group.unknown].forEach(value => row.append(node('td', value)));
      amounts.append(row);
    }
  }
}
function showCase(row) {
  element('case-detail').hidden = false;
  element('case-title').textContent = 'Review ' + row.id;
  element('case-explanation').textContent = 'Recorded justification: ' + row.prediction.justification;
  element('case-warnings').textContent = 'Quality warnings: ' + (row.quality_flags.join('; ') || 'None in the typed feature snapshot.');
  element('case-features').textContent = JSON.stringify(row.features, null, 2);
}
function renderQueue(resetPage = true) {
  if (resetPage) pageIndex = 0;
  element('case-detail').hidden = true;
  const decision = element('decision-filter').value;
  const query = element('case-search').value.trim().toLowerCase();
  matchingCases = filteredRecords().filter(row => row.id.toLowerCase().includes(query) &&
    (decision === 'all' || row.prediction.is_fraud === (decision === 'flagged')));
  matchingCases.sort((first, second) => Number(second.prediction.is_fraud) - Number(first.prediction.is_fraud) || second.prediction.confidence - first.prediction.confidence || first.id.localeCompare(second.id));
  const pageCount = Math.max(1, Math.ceil(matchingCases.length / pageSize));
  pageIndex = Math.min(pageIndex, pageCount - 1);
  const visible = matchingCases.slice(pageIndex * pageSize, (pageIndex + 1) * pageSize);
  element('queue-count').textContent = matchingCases.length + ' matching cases; showing ' + visible.length + '. Export includes all matching cases, not just this page.';
  element('empty-queue').hidden = matchingCases.length !== 0;
  element('page-number').textContent = 'Page ' + (pageIndex + 1) + ' of ' + pageCount;
  element('previous-page').disabled = pageIndex === 0;
  element('next-page').disabled = pageIndex + 1 >= pageCount;
  element('export-cases').disabled = matchingCases.length === 0;
  const body = element('queue-body');
  body.replaceChildren();
  for (const row of visible) {
    const output = node('tr');
    [row.id, row.category + ' / ' + row.channel, money(row.amount, row.currency), row.prediction.is_fraud ? 'Flagged' : 'Not flagged', row.prediction.confidence.toFixed(3), row.quality_flags.length].forEach(value => output.append(node('td', value)));
    const cell = node('td');
    const button = node('button', 'Inspect');
    button.type = 'button';
    button.setAttribute('aria-label', 'Inspect ' + row.id);
    button.addEventListener('click', () => showCase(row));
    cell.append(button);
    output.append(cell);
    body.append(output);
  }
}
function exportRecords() {
  return matchingCases.map(row => row.prediction);
}
element('export-cases').addEventListener('click', () => {
  const blob = new Blob([JSON.stringify(exportRecords(), null, 2)], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const link = node('a');
  link.href = url;
  link.download = 'review_predictions.json';
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
element('previous-page').addEventListener('click', () => {pageIndex--; renderQueue(false);});
element('next-page').addEventListener('click', () => {pageIndex++; renderQueue(false);});
element('decision-filter').addEventListener('change', () => renderQueue());
element('case-search').addEventListener('input', () => renderQueue());
function renderAll() {
  const rows = filteredRecords();
  renderOverview(rows);
  renderHeatmap(rows);
  renderQueue();
}
element('reset-filters').addEventListener('click', () => {
  for (const key of ['category', 'channel', 'currency']) element(key + '-filter').value = '';
  element('decision-filter').value = 'flagged';
  element('case-search').value = '';
  renderAll();
});
function demonstrateBoundary() {
  const note = element('attack-note').value;
  element('note-preview').textContent = note || '(empty note)';
  element('prompt-preview').textContent = JSON.stringify(SNAPSHOT.guardrail.prompt, null, 2);
  element('guardrail-status').textContent = note.length + ' note characters excluded. Verified prompt unchanged. This demonstration does not rescore a transaction.';
}
element('attack-note').addEventListener('input', demonstrateBoundary);
renderAll();
demonstrateBoundary();
