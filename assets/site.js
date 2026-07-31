"use strict";

const CASES = {
  w5: {
    mode: "Documented W5 case",
    rawArea: 1610.02,
    perimeter: 165.4,
    azimuth: 303.8,
    tilt: 15,
    shape: [
      [0.16, 0.28],
      [0.38, 0.12],
      [0.81, 0.33],
      [0.72, 0.79],
      [0.49, 0.88],
      [0.4, 0.73],
      [0.31, 0.78],
      [0.22, 0.58]
    ]
  },
  commercial: {
    mode: "Illustrative commercial fixture",
    rawArea: 2450,
    perimeter: 210,
    azimuth: 180,
    tilt: 10,
    shape: [
      [0.12, 0.22],
      [0.86, 0.22],
      [0.82, 0.78],
      [0.18, 0.78]
    ]
  }
};

const byId = (id) => document.getElementById(id);

const elements = {
  form: byId("estimatorForm"),
  building: byId("building"),
  setback: byId("setback"),
  setbackValue: byId("setbackValue"),
  efficiency: byId("efficiency"),
  efficiencyValue: byId("efficiencyValue"),
  tariff: byId("tariff"),
  tariffValue: byId("tariffValue"),
  caseMode: byId("caseMode"),
  usableArea: byId("usableArea"),
  dcCapacity: byId("dcCapacity"),
  acCapacity: byId("acCapacity"),
  annualYield: byId("annualYield"),
  payback: byId("payback"),
  canvas: byId("roofCanvas")
};

function orientationDerate(azimuthDegrees, tiltDegrees) {
  const wrapped = ((azimuthDegrees - 180 + 180) % 360 + 360) % 360;
  const deviationFromSouth = Math.abs(wrapped - 180);
  const azimuthFactor = Math.cos((deviationFromSouth / 2) * Math.PI / 180);
  const tiltFactor = Math.cos((Math.abs(tiltDegrees - 20) / 2) * Math.PI / 180);
  return Math.max(0.5, azimuthFactor * tiltFactor);
}

function calculate(caseData, setback, efficiencyPercent, tariff) {
  const usableArea = Math.max(0, caseData.rawArea - caseData.perimeter * setback);
  const dcCapacity = usableArea * (efficiencyPercent / 100);
  const acCapacity = dcCapacity / 1.2;
  const annualYield = dcCapacity
    * 5.5
    * 365
    * orientationDerate(caseData.azimuth, caseData.tilt)
    * 0.85;
  const payback = annualYield > 0 && tariff > 0
    ? (dcCapacity * 1000) / (annualYield * tariff)
    : Number.POSITIVE_INFINITY;

  return { usableArea, dcCapacity, acCapacity, annualYield, payback };
}

function formatNumber(value, digits = 2) {
  return value.toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  });
}

function drawRoof(caseData, setback) {
  const canvas = elements.canvas;
  if (!canvas) return;

  const rect = canvas.getBoundingClientRect();
  const scale = Math.max(1, window.devicePixelRatio || 1);
  const width = Math.max(320, Math.round(rect.width));
  const height = Math.max(240, Math.round(rect.height));

  canvas.width = Math.round(width * scale);
  canvas.height = Math.round(height * scale);

  const ctx = canvas.getContext("2d");
  ctx.scale(scale, scale);
  ctx.clearRect(0, 0, width, height);

  const marginX = width * 0.07;
  const marginY = height * 0.08;
  const points = caseData.shape.map(([x, y]) => [
    marginX + x * (width - marginX * 2),
    marginY + y * (height - marginY * 2)
  ]);

  const makePath = (pathPoints) => {
    ctx.beginPath();
    pathPoints.forEach(([x, y], index) => {
      if (index === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.closePath();
  };

  ctx.save();
  makePath(points);
  const fill = ctx.createLinearGradient(0, 0, width, height);
  fill.addColorStop(0, "rgba(24, 189, 244, 0.10)");
  fill.addColorStop(1, "rgba(255, 181, 27, 0.05)");
  ctx.fillStyle = fill;
  ctx.fill();
  ctx.strokeStyle = "#18bdf4";
  ctx.lineWidth = 2.5;
  ctx.shadowColor = "rgba(24, 189, 244, 0.35)";
  ctx.shadowBlur = 14;
  ctx.stroke();
  ctx.restore();

  const center = points.reduce(
    (sum, [x, y]) => [sum[0] + x / points.length, sum[1] + y / points.length],
    [0, 0]
  );
  const insetFactor = Math.min(0.18, 0.035 + setback * 0.017);
  const insetPoints = points.map(([x, y]) => [
    x + (center[0] - x) * insetFactor,
    y + (center[1] - y) * insetFactor
  ]);

  ctx.save();
  makePath(insetPoints);
  ctx.strokeStyle = "#ffb51b";
  ctx.lineWidth = 1.7;
  ctx.setLineDash([7, 6]);
  ctx.stroke();
  ctx.clip();

  const minX = Math.min(...insetPoints.map(([x]) => x));
  const maxX = Math.max(...insetPoints.map(([x]) => x));
  const minY = Math.min(...insetPoints.map(([, y]) => y));
  const maxY = Math.max(...insetPoints.map(([, y]) => y));
  const panelWidth = Math.max(12, width * 0.027);
  const panelHeight = Math.max(8, height * 0.038);
  const gap = 5;

  for (let y = minY + 18; y < maxY - panelHeight - 8; y += panelHeight + gap) {
    for (let x = minX + 18; x < maxX - panelWidth - 8; x += panelWidth + gap) {
      ctx.fillStyle = "rgba(29, 130, 181, 0.72)";
      ctx.fillRect(x, y, panelWidth, panelHeight);
      ctx.strokeStyle = "rgba(123, 220, 255, 0.45)";
      ctx.lineWidth = 0.8;
      ctx.strokeRect(x, y, panelWidth, panelHeight);
    }
  }
  ctx.restore();

  ctx.fillStyle = "#aab8ca";
  ctx.font = `600 ${Math.max(10, Math.round(width * 0.014))}px Consolas, monospace`;
  ctx.fillText(`${formatNumber(caseData.rawArea)} m² raw footprint`, marginX, height - 17);
}

function updateEstimator() {
  if (!elements.form) return;

  const caseData = CASES[elements.building.value];
  const setback = Number(elements.setback.value);
  const efficiency = Number(elements.efficiency.value);
  const tariff = Number(elements.tariff.value);
  const result = calculate(caseData, setback, efficiency, tariff);

  elements.setbackValue.textContent = `${setback.toFixed(2)} m`;
  elements.efficiencyValue.textContent = `${efficiency.toFixed(1)}%`;
  elements.tariffValue.textContent = `${tariff.toFixed(2)} / kWh`;
  elements.caseMode.textContent = caseData.mode;
  elements.usableArea.textContent = `${formatNumber(result.usableArea)} m²`;
  elements.dcCapacity.textContent = `${formatNumber(result.dcCapacity)} kW`;
  elements.acCapacity.textContent = `${formatNumber(result.acCapacity)} kW`;
  elements.annualYield.textContent = `${formatNumber(result.annualYield, 0)} kWh`;
  elements.payback.textContent = Number.isFinite(result.payback)
    ? `${result.payback.toFixed(2)} years`
    : "—";

  drawRoof(caseData, setback);
}

function activateTab(nextTab) {
  const tabs = Array.from(document.querySelectorAll('[role="tab"][aria-controls]'));
  tabs.forEach((tab) => {
    const selected = tab === nextTab;
    tab.setAttribute("aria-selected", String(selected));
    tab.tabIndex = selected ? 0 : -1;
    const panel = byId(tab.getAttribute("aria-controls"));
    if (panel) panel.hidden = !selected;
  });
}

function bindTabs() {
  const tabs = Array.from(document.querySelectorAll('[role="tab"][aria-controls]'));
  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => activateTab(tab));
    tab.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      let nextIndex = index;
      if (event.key === "ArrowRight") nextIndex = (index + 1) % tabs.length;
      if (event.key === "ArrowLeft") nextIndex = (index - 1 + tabs.length) % tabs.length;
      if (event.key === "Home") nextIndex = 0;
      if (event.key === "End") nextIndex = tabs.length - 1;
      tabs[nextIndex].focus();
      activateTab(tabs[nextIndex]);
    });
  });
}

function bindCopyButtons() {
  document.querySelectorAll("[data-copy-target]").forEach((button) => {
    button.addEventListener("click", async () => {
      const target = byId(button.dataset.copyTarget);
      if (!target) return;

      try {
        await navigator.clipboard.writeText(target.textContent.trim());
        const original = button.textContent;
        button.textContent = "Copied";
        window.setTimeout(() => {
          button.textContent = original;
        }, 1800);
      } catch {
        button.textContent = "Select text";
      }
    });
  });
}

let resizeFrame = 0;
function bindEstimator() {
  if (!elements.form) return;
  elements.form.addEventListener("input", updateEstimator);
  elements.form.addEventListener("change", updateEstimator);
  window.addEventListener("resize", () => {
    window.cancelAnimationFrame(resizeFrame);
    resizeFrame = window.requestAnimationFrame(updateEstimator);
  });
  updateEstimator();
}

bindEstimator();
bindTabs();
bindCopyButtons();
