const els = {
  numProcesses: document.getElementById('numProcesses'),
  eventsPerProcess: document.getElementById('eventsPerProcess'),
  messageProbability: document.getElementById('messageProbability'),
  messageProbabilityValue: document.getElementById('messageProbabilityValue'),
  seed: document.getElementById('seed'),
  runBtn: document.getElementById('runBtn'),
  status: document.getElementById('status'),
  svg: document.getElementById('timeline'),
  finalClocks: document.getElementById('finalClocks'),
};

els.messageProbability.addEventListener('input', () => {
  els.messageProbabilityValue.textContent = els.messageProbability.value;
});

els.runBtn.addEventListener('click', runSimulation);

async function runSimulation() {
  setStatus('Running simulation…', false);
  els.runBtn.disabled = true;

  const body = {
    num_processes: parseInt(els.numProcesses.value, 10),
    events_per_process: parseInt(els.eventsPerProcess.value, 10),
    message_probability: parseFloat(els.messageProbability.value),
    seed: els.seed.value === '' ? null : parseInt(els.seed.value, 10),
  };

  try {
    const res = await fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) {
      setStatus(data.error || 'Simulation failed.', true);
      return;
    }
    setStatus(`Rendered ${data.messages.length} message(s) across ${data.num_processes} processes.`, false);
    renderTimeline(data);
    renderFinalClocks(data.final_clocks);
  } catch (err) {
    setStatus('Could not reach the server. Is the backend running?', true);
  } finally {
    els.runBtn.disabled = false;
  }
}

function setStatus(text, isError) {
  els.status.textContent = text;
  els.status.classList.toggle('error', !!isError);
}

function renderFinalClocks(clocks) {
  els.finalClocks.innerHTML = '';
  clocks.forEach((c, i) => {
    const chip = document.createElement('div');
    chip.className = 'clock-chip';
    chip.innerHTML = `<span class="label">process ${i}</span><span class="value">${c}</span>`;
    els.finalClocks.appendChild(chip);
  });
}

function renderTimeline(data) {
  const svg = d3.select(els.svg);
  svg.selectAll('*').remove();

  const rowHeight = 90;
  const leftMargin = 90;
  const rightMargin = 40;
  const topMargin = 30;
  const colWidth = 70;

  const maxSeq = Math.max(...data.timelines.map(tl => tl.length), 1);
  const width = leftMargin + rightMargin + maxSeq * colWidth;
  const height = topMargin + data.num_processes * rowHeight;

  svg.attr('viewBox', `0 0 ${width} ${height}`);

  const colorFor = kind => ({
    internal: 'var(--muted)',
    send: 'var(--teal)',
    receive: 'var(--amber)',
  }[kind] || '#888');

  // Resolve CSS vars to actual colors for SVG (SVG doesn't read CSS custom props reliably cross-browser)
  const cs = getComputedStyle(document.documentElement);
  const colors = {
    internal: cs.getPropertyValue('--muted').trim(),
    send: cs.getPropertyValue('--teal').trim(),
    receive: cs.getPropertyValue('--amber').trim(),
    line: cs.getPropertyValue('--panel-line').trim(),
    text: cs.getPropertyValue('--text').trim(),
    muted: cs.getPropertyValue('--muted').trim(),
  };

  // Process lanes + labels
  const laneG = svg.append('g');
  data.timelines.forEach((tl, p) => {
    const y = topMargin + p * rowHeight + rowHeight / 2;
    laneG.append('line')
      .attr('x1', leftMargin).attr('x2', width - rightMargin)
      .attr('y1', y).attr('y2', y)
      .attr('stroke', colors.line).attr('stroke-width', 1);
    laneG.append('text')
      .attr('x', 10).attr('y', y)
      .attr('dy', '0.35em')
      .attr('fill', colors.text)
      .attr('font-family', 'JetBrains Mono, monospace')
      .attr('font-size', '13px')
      .text(`P${p}`);
  });

  // Position lookup: (process, seq) -> {x, y}
  const posOf = (p, seq) => ({
    x: leftMargin + seq * colWidth + colWidth / 2,
    y: topMargin + p * rowHeight + rowHeight / 2,
  });

  // Events
  data.timelines.forEach((tl, p) => {
    tl.forEach(ev => {
      const { x, y } = posOf(p, ev.seq);
      const g = svg.append('g');
      g.append('circle')
        .attr('cx', x).attr('cy', y).attr('r', 7)
        .attr('fill', colors[ev.kind]);
      g.append('text')
        .attr('x', x).attr('y', y - 16)
        .attr('text-anchor', 'middle')
        .attr('fill', colors[ev.kind])
        .attr('font-family', 'JetBrains Mono, monospace')
        .attr('font-weight', 700)
        .attr('font-size', '13px')
        .text(ev.clock);
    });
  });

  // Message arrows (send -> receive)
  const eventIndex = {};
  data.timelines.forEach((tl, p) => {
    tl.forEach(ev => { eventIndex[`${p}-${ev.message_id}-${ev.kind}`] = ev; });
  });

  data.messages.forEach(m => {
    const sendEv = data.timelines[m.from].find(e => e.kind === 'send' && e.message_id === m.id);
    const recvEv = data.timelines[m.to].find(e => e.kind === 'receive' && e.message_id === m.id);
    if (!sendEv || !recvEv) return;
    const p1 = posOf(m.from, sendEv.seq);
    const p2 = posOf(m.to, recvEv.seq);

    svg.append('line')
      .attr('x1', p1.x).attr('y1', p1.y)
      .attr('x2', p2.x).attr('y2', p2.y)
      .attr('stroke', colors.send)
      .attr('stroke-width', 1.5)
      .attr('stroke-dasharray', '4 3')
      .attr('marker-end', 'url(#arrowhead)');
  });

  // Arrowhead marker
  svg.append('defs').append('marker')
    .attr('id', 'arrowhead')
    .attr('viewBox', '0 0 10 10')
    .attr('refX', 8).attr('refY', 5)
    .attr('markerWidth', 6).attr('markerHeight', 6)
    .attr('orient', 'auto-start-reverse')
    .append('path')
    .attr('d', 'M0,0 L10,5 L0,10 Z')
    .attr('fill', colors.send);
}

// Run once on load with defaults
runSimulation();
