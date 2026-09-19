const FEEDBACK_KEY = 'fraud-sentinel.feedback.v1.' + SNAPSHOT.checkpoint.predictions_sha256;
const feedbackDecisions = ['needs_review', 'suspected_fraud', 'likely_legitimate', 'inconclusive'];
let feedbackLedger = {schema_version: 1, checkpoint: SNAPSHOT.checkpoint, events: []};
let feedbackRaw = null;
let feedbackError = '';
let selectedFeedbackCase = null;
function exactKeys(value, fields) {
  return value && typeof value === 'object' && !Array.isArray(value) && Object.keys(value).sort().join('|') === [...fields].sort().join('|');
}
function validateFeedback(ledger) {
  if (!exactKeys(ledger, ['schema_version', 'checkpoint', 'events']) || ledger.schema_version !== 1 ||
      !exactKeys(ledger.checkpoint, Object.keys(SNAPSHOT.checkpoint)) ||
      Object.keys(SNAPSHOT.checkpoint).some(key => ledger.checkpoint[key] !== SNAPSHOT.checkpoint[key])) throw Error('Feedback belongs to another checkpoint or unsupported schema.');
  if (!Array.isArray(ledger.events) || ledger.events.length > 5000) throw Error('Maximum 5,000 feedback events per checkpoint.');
  const allowed = new Set(SNAPSHOT.records.map(row => row.id));
  const seen = new Set();
  for (const event of ledger.events) {
    if (!exactKeys(event, ['event_id', 'transaction_id', 'analyst', 'decision', 'note', 'evidence_reference', 'recorded_at', 'label_status', 'eligible_for_training'])) throw Error('Invalid event fields.');
    if (typeof event.event_id !== 'string' || event.event_id.length < 8 || event.event_id.length > 80 || /[^a-zA-Z0-9_-]/.test(event.event_id) || seen.has(event.event_id)) throw Error('Invalid or duplicate event ID.');
    seen.add(event.event_id);
    if (!allowed.has(event.transaction_id) || !feedbackDecisions.includes(event.decision)) throw Error('Unknown transaction or decision.');
    for (const [field, limit, required] of [['analyst', 80, true], ['note', 2000, true], ['evidence_reference', 300, false]]) {
      if (typeof event[field] !== 'string' || event[field].length > limit || (required && !event[field].trim())) throw Error('Invalid ' + field + '.');
    }
    if (typeof event.recorded_at !== 'string' || event.recorded_at.startsWith('0000') || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(event.recorded_at) || !Number.isFinite(Date.parse(event.recorded_at)) || new Date(event.recorded_at).toISOString() !== event.recorded_at) throw Error('Invalid UTC timestamp.');
    if (event.label_status !== 'unverified_analyst_feedback' || event.eligible_for_training !== false) throw Error('Feedback is not verified ground truth or training-ready.');
  }
  return ledger;
}
function loadFeedback() {
  try {
    const raw = localStorage.getItem(FEEDBACK_KEY);
    const ledger = raw === null ? {schema_version: 1, checkpoint: SNAPSHOT.checkpoint, events: []} : validateFeedback(JSON.parse(raw));
    feedbackLedger = ledger;
    feedbackRaw = raw;
    feedbackError = '';
  } catch (error) {
    feedbackError = 'Feedback storage unavailable or invalid. Existing storage was not overwritten. ' + error.message;
  }
}
function persistFeedback(ledger) {
  if (feedbackError) throw Error(feedbackError);
  validateFeedback(ledger);
  if (localStorage.getItem(FEEDBACK_KEY) !== feedbackRaw) {
    loadFeedback();
    throw Error('Feedback changed in another tab. Review the reloaded history, then save again.');
  }
  const raw = JSON.stringify(ledger);
  localStorage.setItem(FEEDBACK_KEY, raw);
  feedbackRaw = raw;
  feedbackLedger = ledger;
}
function latestFeedback(identifier) {
  return feedbackLedger.events.filter(event => event.transaction_id === identifier).at(-1);
}
function feedbackSummary() {
  const reviewed = new Set(feedbackLedger.events.map(event => event.transaction_id)).size;
  element('feedback-summary').textContent = feedbackError || feedbackLedger.events.length + ' history events across ' + reviewed + ' reviewed transactions. Stored only in this browser. Zero verified training labels.';
  element('feedback-export').disabled = feedbackLedger.events.length === 0;
  element('feedback-save').disabled = Boolean(feedbackError);
}
function showFeedback(row) {
  selectedFeedbackCase = row;
  const latest = latestFeedback(row.id);
  element('feedback-decision').value = latest ? latest.decision : 'needs_review';
  element('feedback-note').value = '';
  element('feedback-evidence').value = '';
  const history = element('feedback-history');
  history.replaceChildren();
  for (const event of feedbackLedger.events.filter(item => item.transaction_id === row.id)) {
    const item = node('li');
    item.append(node('strong', event.decision.replaceAll('_', ' ') + ' — ' + event.analyst),
      node('p', event.recorded_at + ' (self-reported analyst; browser clock)'), node('p', event.note));
    if (event.evidence_reference) item.append(node('p', 'Evidence reference: ' + event.evidence_reference));
    history.append(item);
  }
  if (!history.children.length) history.append(node('li', 'No feedback recorded for this case.'));
  feedbackSummary();
}
function saveFeedback() {
  if (!selectedFeedbackCase) throw Error('Inspect a case before saving feedback.');
  const analyst = element('feedback-analyst').value.trim();
  const decision = element('feedback-decision').value;
  const note = element('feedback-note').value.trim();
  const evidence = element('feedback-evidence').value.trim();
  const latest = latestFeedback(selectedFeedbackCase.id);
  if (latest && latest.analyst === analyst && latest.decision === decision && latest.note === note && latest.evidence_reference === evidence) return false;
  const event = {event_id: crypto.randomUUID(), transaction_id: selectedFeedbackCase.id, analyst,
    decision, note, evidence_reference: evidence, recorded_at: new Date().toISOString(),
    label_status: 'unverified_analyst_feedback', eligible_for_training: false};
  persistFeedback({...feedbackLedger, events: [...feedbackLedger.events, event]});
  return true;
}
function mergeFeedback(incoming) {
  validateFeedback(incoming);
  const events = [...feedbackLedger.events];
  const existing = new Map(events.map(event => [event.event_id, event]));
  for (const event of incoming.events) {
    if (existing.has(event.event_id)) {
      if (Object.keys(event).some(key => event[key] !== existing.get(event.event_id)[key])) throw Error('Conflicting content for an existing event ID.');
    } else events.push(event);
  }
  const count = events.length - feedbackLedger.events.length;
  persistFeedback({...feedbackLedger, events});
  return count;
}
function downloadFeedback() {
  const blob = new Blob([JSON.stringify(feedbackLedger, null, 2)], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const link = node('a');
  link.href = url;
  link.download = 'analyst_feedback.json';
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function initFeedback() {
  feedbackSummary();
  element('feedback-form').addEventListener('submit', event => {
    event.preventDefault();
    try {
      const added = saveFeedback();
      const current = selectedFeedbackCase;
      renderQueue(false);
      showCase(current);
      element('feedback-status').textContent = added ? 'Saved locally. Model prediction unchanged. Export a backup before leaving this browser.' : 'Identical feedback already saved; no duplicate event added.';
    } catch (error) {element('feedback-status').textContent = 'Not saved: ' + error.message; feedbackSummary();}
  });
  element('feedback-export').addEventListener('click', downloadFeedback);
  element('feedback-import').addEventListener('change', async event => {
    const file = event.target.files[0];
    if (!file) return;
    try {
      if (file.size > 20000000) throw Error('File exceeds 20 MB.');
      const added = mergeFeedback(JSON.parse(await file.text()));
      feedbackSummary();
      renderQueue(false);
      element('feedback-status').textContent = 'Imported ' + added + ' new events. Existing event IDs are deduplicated; imported new events are appended in file order.';
    } catch (error) {element('feedback-status').textContent = 'Import rejected: ' + error.message;}
    event.target.value = '';
  });
  window.addEventListener('storage', event => {
    if (event.key === FEEDBACK_KEY || event.key === null) {
      loadFeedback(); feedbackSummary(); renderQueue(false);
      element('feedback-status').textContent = 'Feedback changed in another tab. Reopen the case before editing.';
    }
  });
}
loadFeedback();
