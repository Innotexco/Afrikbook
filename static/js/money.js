/**
 * Afrikbook money helpers
 *
 * Display: formatMoney / NCFormat for report text (not live calc inputs).
 * Math:    parseMoney always strips commas — use this instead of parseFloat for money.
 * Submit:  commas stripped from form/AJAX so DB never stores them.
 *
 * IMPORTANT: Never inject commas into calculation inputs (New Sales, Purchase,
 * invoice grids, #total / #sub-total, unit[], amount[], etc.). That breaks
 * parseFloat and live line-total updates.
 */
(function (window, document, $) {
  "use strict";

  var MONEY_HEADER_RE =
    /amount|price|total|cost|paid|expected|outstanding|balance|sales|purchase|salary|discount|vat|fee|charge|credit|debit/i;

  // Fields used in live arithmetic — never auto-format these INPUT values
  var CALC_INPUT_NAME_RE =
    /^(amount\[\]|unit\[\]|discount\[\]|qty\[\]|purchaseP|purchasep|item\[\]|desc\[\]|vat|sub-total|sub_total|total|part_payment_amount|transfer_amount|cash_amount|shipping_cost|payment_amount|cost|Discount)$/i;

  var CALC_INPUT_ID_RE =
    /^(total|sub-total|sub_total|amount_paid|amount_expected|total-cost|discount2|vat|part_payment_amount|transfer_amount|cash_amount|payment_amount|Discount|qty|unit|amount|discount)$/i;

  function parseMoney(value) {
    if (value === null || value === undefined || value === "") return 0;
    if (typeof value === "number") {
      return isFinite(value) ? value : 0;
    }
    var s = String(value)
      .replace(/[₦$£€]/g, "")
      .replace(/,/g, "")
      .replace(/\s/g, "")
      .trim();
    if (!s || s === "-") return 0;
    var n = parseFloat(s);
    return isFinite(n) ? n : 0;
  }

  function formatMoney(value, places) {
    places = places === undefined || places === null ? 2 : places;
    var n = parseMoney(value);
    try {
      return new Intl.NumberFormat("en-US", {
        minimumFractionDigits: places,
        maximumFractionDigits: places,
      }).format(n);
    } catch (e) {
      return n.toFixed(places).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }
  }

  window.parseMoney = parseMoney;
  window.formatMoney = formatMoney;
  window.NCFormat = formatMoney;

  function looksLikePlainNumber(text) {
    if (text === null || text === undefined) return false;
    var s = String(text).trim();
    if (!s) return false;
    if (/[a-zA-Z/%]/.test(s)) return false;
    return /^-?\d{1,3}(,\d{3})*(\.\d+)?$/.test(s) || /^-?\d+(\.\d+)?$/.test(s);
  }

  function isCalcInput(el) {
    if (!el || !/^(INPUT|TEXTAREA)$/i.test(el.tagName)) return false;
    var name = el.name || "";
    var id = el.id || "";
    if (el.getAttribute("data-money-calc") === "1") return true;
    if (el.getAttribute("data-money-display") === "1") return false;
    if (CALC_INPUT_ID_RE.test(id)) return true;
    if (CALC_INPUT_NAME_RE.test(name)) return true;
    // Invoice / sales line grids
    if (name === "unit[]" || name === "amount[]" || name === "discount[]" || name === "qty[]") {
      return true;
    }
    // Inside a form that posts invoice lines
    var form = el.form || el.closest && el.closest("form");
    if (form && form.querySelector && form.querySelector('input[name="amount[]"], input[name="unit[]"]')) {
      if (MONEY_HEADER_RE.test(name) || MONEY_HEADER_RE.test(id) || /amount|unit|total|discount|vat|price/i.test(name + id)) {
        return true;
      }
    }
    return false;
  }

  function stripCommasFromInput(el) {
    if (!el || el.value === undefined || el.value === null) return;
    if (String(el.value).indexOf(",") === -1) return;
    if (!looksLikePlainNumber(el.value)) return;
    var n = parseMoney(el.value);
    // Keep raw number string suitable for parseFloat / calc (no forced 2dp on qty)
    var name = el.name || "";
    if (name === "qty[]" || el.id === "qty") {
      el.value = String(n);
    } else {
      el.value = String(n);
    }
  }

  /** Remove commas from all calc/money inputs so live UI math keeps working */
  function sanitizeCalcInputs(root) {
    root = root || document;
    var fields = root.querySelectorAll("input, textarea");
    fields.forEach(function (el) {
      if (isCalcInput(el) || (el.value && String(el.value).indexOf(",") !== -1 && looksLikePlainNumber(el.value))) {
        // Always strip commas from numeric-looking inputs used in forms
        if (isCalcInput(el) || (el.form && looksLikePlainNumber(el.value))) {
          stripCommasFromInput(el);
        }
      }
    });
  }

  function formatElementText(el) {
    if (!el || el.getAttribute("data-money-skip") === "1") return;
    if (/^(INPUT|SELECT|TEXTAREA)$/i.test(el.tagName)) return;
    // Skip cells that are part of editable invoice grids
    if (el.closest && el.closest('input[name="amount[]"], form:has(input[name="amount[]"])')) {
      // still allow pure text report cells; only skip if sibling inputs in same cell
    }
    if (el.querySelector && el.querySelector("input, select, textarea")) return;

    var text = (el.textContent || "").trim();
    if (!looksLikePlainNumber(text)) return;
    el.textContent = formatMoney(text);
    el.setAttribute("data-money-formatted", "1");
  }

  function formatMoneyClassTargets(root) {
    root = root || document;
    var nodes = root.querySelectorAll(
      ".money, .money-value, [data-money], .currency-amount"
    );
    nodes.forEach(function (el) {
      // Inputs: only format when explicitly marked for display (not calc)
      if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
        if (isCalcInput(el)) {
          stripCommasFromInput(el);
          return;
        }
        if (el.getAttribute("data-money-display") === "1" || el.getAttribute("data-money-format") === "1") {
          if (el.value !== "" && looksLikePlainNumber(el.value)) {
            el.value = formatMoney(el.value);
          }
        }
        return;
      }
      formatElementText(el);
    });
  }

  function formatKnownTotalIds(root) {
    root = root || document;
    // Only non-input elements or explicit display-only inputs
    var ids = [
      "amount_total",
      "sales_total",
      "purchase_total",
      "grandTotal",
      "total-amount",
      "amount-paid",
    ];
    ids.forEach(function (id) {
      var el = root.getElementById ? root.getElementById(id) : null;
      if (!el) return;
      if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
        if (el.getAttribute("data-money-display") === "1") {
          if (el.value !== "" && looksLikePlainNumber(el.value)) {
            el.value = formatMoney(el.value);
          }
        } else {
          // Never format live calc totals like #total / #sub-total
          stripCommasFromInput(el);
        }
        return;
      }
      formatElementText(el);
    });

    // Explicitly unformat known calc totals if commas snuck in
    ["total", "sub-total", "sub_total", "discount2", "part_payment_amount"].forEach(function (id) {
      var el = root.getElementById ? root.getElementById(id) : null;
      if (el && (el.tagName === "INPUT" || el.tagName === "TEXTAREA")) {
        stripCommasFromInput(el);
      }
    });
  }

  function moneyColumnIndexes(table) {
    var indexes = [];
    var headers = table.querySelectorAll("thead th, thead td");
    headers.forEach(function (th, idx) {
      var label = (th.textContent || "").trim();
      if (
        MONEY_HEADER_RE.test(label) &&
        !/qty|quantity|sn|s\/n|date|id|name|code|item|desc/i.test(label)
      ) {
        indexes.push(idx);
      }
      if (th.classList.contains("money-col") || th.getAttribute("data-money-col") === "1") {
        if (indexes.indexOf(idx) === -1) indexes.push(idx);
      }
    });
    return indexes;
  }

  function formatTableMoneyColumns(root) {
    root = root || document;
    var tables = root.querySelectorAll("table");
    tables.forEach(function (table) {
      if (table.getAttribute("data-money-skip") === "1") return;
      // Skip invoice / sales entry grids (they have unit[] / amount[])
      if (table.querySelector('input[name="amount[]"], input[name="unit[]"], input[name="qty[]"]')) {
        return;
      }
      var cols = moneyColumnIndexes(table);
      if (!cols.length) return;
      var rows = table.querySelectorAll("tbody tr");
      rows.forEach(function (tr) {
        cols.forEach(function (colIdx) {
          var cell = tr.children[colIdx];
          if (!cell) return;
          // Never format inputs inside tables — report text cells only
          if (cell.querySelector("input, select, textarea")) return;
          formatElementText(cell);
        });
      });
    });
  }

  function isMoneyInput(el) {
    if (!el || !/^(INPUT|TEXTAREA)$/i.test(el.tagName)) return false;
    if (isCalcInput(el)) return true; // for submit strip only
    if (el.type && /checkbox|radio|file|hidden|date|time|email|password|button|submit/.test(el.type)) {
      if (el.type === "hidden" && el.getAttribute("data-money") === "1") return true;
      return false;
    }
    if (el.classList && el.classList.contains("money-input")) return true;
    if (el.getAttribute("data-money") === "1") return true;
    if (el.getAttribute("data-money-display") === "1") return true;
    if (el.getAttribute("data-money-format") === "1") return true;
    return false;
  }

  function unformatMoneyInputs(form) {
    var scope = form || document;
    var fields = scope.querySelectorAll("input, textarea");
    fields.forEach(function (el) {
      if (!el.value || String(el.value).indexOf(",") === -1) return;
      if (looksLikePlainNumber(el.value)) {
        el.value = String(parseMoney(el.value));
      }
    });
  }

  function bindMoneyInputUX(root) {
    root = root || document;
    var fields = root.querySelectorAll("input, textarea");
    fields.forEach(function (el) {
      // Only explicit display/format fields get focus/blur comma UX
      var wantFormat =
        el.getAttribute("data-money-format") === "1" ||
        el.getAttribute("data-money-display") === "1";
      if (!wantFormat) return;
      if (isCalcInput(el)) return;
      if (el.getAttribute("data-money-bound") === "1") return;
      el.setAttribute("data-money-bound", "1");

      el.addEventListener("focus", function () {
        if (el.value && String(el.value).indexOf(",") !== -1) {
          el.value = String(parseMoney(el.value));
        }
      });

      el.addEventListener("blur", function () {
        if (el.value === "" || el.value === null) return;
        el.value = formatMoney(el.value);
      });
    });
  }

  function bindFormSubmitSanitize() {
    document.addEventListener(
      "submit",
      function (e) {
        var form = e.target;
        if (!form || form.tagName !== "FORM") return;
        unformatMoneyInputs(form);
      },
      true
    );

    if ($ && $.ajaxPrefilter) {
      $.ajaxPrefilter(function (options) {
        if (!options.data) return;
        if (typeof options.data === "string") {
          options.data = options.data.replace(/=([^&]*)/g, function (m, val) {
            try {
              var decoded = decodeURIComponent(val.replace(/\+/g, " "));
              if (decoded.indexOf(",") !== -1 && looksLikePlainNumber(decoded)) {
                return "=" + encodeURIComponent(String(parseMoney(decoded)));
              }
            } catch (err) {}
            return m;
          });
        } else if (typeof options.data === "object" && !(options.data instanceof FormData)) {
          Object.keys(options.data).forEach(function (k) {
            var v = options.data[k];
            if (typeof v === "string" && v.indexOf(",") !== -1 && looksLikePlainNumber(v)) {
              options.data[k] = String(parseMoney(v));
            }
          });
        }
      });
    }
  }

  function runFormatPass(root) {
    try {
      // Always strip commas from calc fields first (fixes prior formatting)
      sanitizeCalcInputs(root);
      formatMoneyClassTargets(root);
      formatKnownTotalIds(root);
      formatTableMoneyColumns(root);
      bindMoneyInputUX(root);
    } catch (e) {
      if (window.console && console.warn) console.warn("[money.js]", e);
    }
  }

  function init() {
    bindFormSubmitSanitize();
    runFormatPass(document);

    if ($ && $(document).ajaxComplete) {
      $(document).ajaxComplete(function () {
        setTimeout(function () {
          // After AJAX: only sanitize calc inputs + format report tables
          sanitizeCalcInputs(document);
          formatMoneyClassTargets(document);
          formatTableMoneyColumns(document);
        }, 50);
      });
    }

    // Light mutation observer — only when new nodes added; always re-sanitize calc inputs
    if (window.MutationObserver) {
      var obs = new MutationObserver(function (mutations) {
        var need = false;
        mutations.forEach(function (m) {
          if (m.addedNodes && m.addedNodes.length) need = true;
        });
        if (need) {
          clearTimeout(window.__moneyFmtTimer);
          window.__moneyFmtTimer = setTimeout(function () {
            sanitizeCalcInputs(document);
            formatTableMoneyColumns(document);
            formatMoneyClassTargets(document);
          }, 100);
        }
      });
      obs.observe(document.body, { childList: true, subtree: true });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.refreshMoneyFormats = function (root) {
    runFormatPass(root || document);
  };
  window.unformatMoneyInputs = unformatMoneyInputs;
  window.sanitizeCalcInputs = sanitizeCalcInputs;
})(window, document, window.jQuery);
