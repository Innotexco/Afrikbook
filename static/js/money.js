/**
 * Afrikbook money helpers
 * - NCFormat / formatMoney: display with thousand separators
 * - parseMoney: strip commas for math / AJAX / submit
 * - Auto-format table money columns and common total fields
 * - Strip commas from form fields before submit so DB never sees commas
 */
(function (window, document, $) {
  "use strict";

  var MONEY_HEADER_RE =
    /amount|price|total|cost|paid|expected|outstanding|balance|sales|purchase|salary|discount|vat|fee|charge|credit|debit/i;

  var MONEY_INPUT_NAME_RE =
    /amount|price|total|cost|paid|expected|salary|discount|vat|balance|unit|transfer|cash|shipping|payment|part_payment|fee|charge|purchasep/i;

  var MONEY_INPUT_ID_RE =
    /^(total|sub-total|sub_total|amount_paid|amount_expected|total-cost|balance|credit|debit|amount_total|payment_amount|Discount|discount2|part_payment_amount|transfer_amount|cash_amount|grandTotal)$/i;

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

  // Global aliases (project already calls NCFormat in several places)
  window.parseMoney = parseMoney;
  window.formatMoney = formatMoney;
  window.NCFormat = formatMoney;

  function isAlreadyFormatted(text) {
    return typeof text === "string" && text.indexOf(",") !== -1;
  }

  function looksLikePlainNumber(text) {
    if (text === null || text === undefined) return false;
    var s = String(text).trim();
    if (!s) return false;
    // Skip dates, codes, percentages, pure integers that are SN-like handled separately
    if (/[a-zA-Z/%]/.test(s)) return false;
    // Plain number or already comma-formatted number
    return /^-?\d{1,3}(,\d{3})*(\.\d+)?$/.test(s) || /^-?\d+(\.\d+)?$/.test(s);
  }

  function formatElementText(el) {
    if (!el || el.getAttribute("data-money-skip") === "1") return;
    // Skip inputs/selects/textarea here (handled separately)
    if (/^(INPUT|SELECT|TEXTAREA)$/i.test(el.tagName)) return;

    var text = (el.textContent || "").trim();
    if (!looksLikePlainNumber(text)) return;
    // Avoid reformatting empty / zero placeholders unnecessarily if marked
    el.textContent = formatMoney(text);
    el.setAttribute("data-money-formatted", "1");
  }

  function formatMoneyClassTargets(root) {
    root = root || document;
    var nodes = root.querySelectorAll(
      ".money, .money-value, [data-money], .currency-amount"
    );
    nodes.forEach(function (el) {
      if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
        if (el.value !== "" && looksLikePlainNumber(el.value)) {
          el.value = formatMoney(el.value);
        }
      } else {
        formatElementText(el);
      }
    });
  }

  function formatKnownTotalIds(root) {
    root = root || document;
    var ids = [
      "amount_total",
      "total",
      "sub-total",
      "amount_paid",
      "amount_expected",
      "total-cost",
      "balance",
      "credit",
      "debit",
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
        // Readonly display fields get commas; editable ones get commas on blur only
        if (el.readOnly || el.disabled || el.getAttribute("data-money-display") === "1") {
          if (el.value !== "" && looksLikePlainNumber(el.value)) {
            el.value = formatMoney(el.value);
          }
        }
      } else {
        formatElementText(el);
      }
    });
  }

  function moneyColumnIndexes(table) {
    var indexes = [];
    var headers = table.querySelectorAll("thead th, thead td");
    headers.forEach(function (th, idx) {
      var label = (th.textContent || "").trim();
      if (MONEY_HEADER_RE.test(label) && !/qty|quantity|sn|s\/n|date|id|name|code|item|desc/i.test(label)) {
        indexes.push(idx);
      }
      // Explicit overrides via class on header
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
      var cols = moneyColumnIndexes(table);
      if (!cols.length) return;
      var rows = table.querySelectorAll("tbody tr");
      rows.forEach(function (tr) {
        cols.forEach(function (colIdx) {
          var cell = tr.children[colIdx];
          if (!cell) return;
          // Prefer formatting text; if cell has a single readonly input, format its value for display
          var input = cell.querySelector("input");
          if (input && (input.readOnly || input.disabled)) {
            if (input.value !== "" && looksLikePlainNumber(input.value)) {
              input.value = formatMoney(input.value);
            }
            return;
          }
          if (input) return; // editable — leave raw for typing
          formatElementText(cell);
        });
      });
    });
  }

  function isMoneyInput(el) {
    if (!el || !/^(INPUT|TEXTAREA)$/i.test(el.tagName)) return false;
    if (el.type && /checkbox|radio|file|hidden|date|time|email|password|button|submit/.test(el.type)) {
      // Allow hidden totals if explicitly marked
      if (el.type === "hidden" && el.getAttribute("data-money") === "1") return true;
      if (el.type === "hidden") return false;
      return false;
    }
    var name = el.name || "";
    var id = el.id || "";
    var cls = el.className || "";
    if (el.classList && el.classList.contains("money-input")) return true;
    if (el.getAttribute("data-money") === "1") return true;
    if (MONEY_INPUT_ID_RE.test(id)) return true;
    if (MONEY_INPUT_NAME_RE.test(name)) return true;
    if (/\bmoney\b/.test(cls)) return true;
    // unit[] is unit price in invoice grids
    if (name === "unit[]" || name === "amount[]" || name === "discount[]") return true;
    return false;
  }

  function unformatMoneyInputs(form) {
    var scope = form || document;
    var fields = scope.querySelectorAll("input, textarea");
    fields.forEach(function (el) {
      if (!isMoneyInput(el) && !(el.value && String(el.value).indexOf(",") !== -1 && looksLikePlainNumber(el.value))) {
        // Still strip commas from any field whose value is clearly a formatted number
        if (el.value && String(el.value).indexOf(",") !== -1) {
          var stripped = String(el.value).replace(/,/g, "").replace(/[₦$£€\s]/g, "");
          if (/^-?\d+(\.\d+)?$/.test(stripped)) {
            el.value = stripped;
          }
        }
        return;
      }
      if (el.value && String(el.value).indexOf(",") !== -1) {
        el.value = String(parseMoney(el.value));
        // keep 2dp for money-ish fields
        if (isMoneyInput(el)) {
          var n = parseMoney(el.value);
          el.value = n.toFixed(2);
        }
      }
    });
  }

  function bindMoneyInputUX(root) {
    root = root || document;
    var fields = root.querySelectorAll("input, textarea");
    fields.forEach(function (el) {
      if (!isMoneyInput(el)) return;
      if (el.getAttribute("data-money-bound") === "1") return;
      el.setAttribute("data-money-bound", "1");

      el.addEventListener("focus", function () {
        if (el.value && String(el.value).indexOf(",") !== -1) {
          el.value = String(parseMoney(el.value));
        }
      });

      el.addEventListener("blur", function () {
        if (el.value === "" || el.value === null) return;
        // Format for display while editing forms (readonly or display mode preferred)
        // For active data-entry unit/amount grids, only format if data-money-format="1"
        if (
          el.readOnly ||
          el.disabled ||
          el.getAttribute("data-money-format") === "1" ||
          el.getAttribute("data-money-display") === "1" ||
          MONEY_INPUT_ID_RE.test(el.id || "")
        ) {
          el.value = formatMoney(el.value);
        }
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

    // jQuery AJAX: strip commas from data objects when possible
    if ($ && $.ajaxPrefilter) {
      $.ajaxPrefilter(function (options) {
        if (!options.data) return;
        if (typeof options.data === "string") {
          // application/x-www-form-urlencoded — strip commas from values
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

    // Re-format after AJAX that rewrites tables
    if ($ && $(document).ajaxComplete) {
      $(document).ajaxComplete(function () {
        setTimeout(function () {
          runFormatPass(document);
        }, 50);
      });
    }

    // Observe dynamic table body changes
    if (window.MutationObserver) {
      var obs = new MutationObserver(function (mutations) {
        var need = false;
        mutations.forEach(function (m) {
          if (m.addedNodes && m.addedNodes.length) need = true;
        });
        if (need) {
          clearTimeout(window.__moneyFmtTimer);
          window.__moneyFmtTimer = setTimeout(function () {
            runFormatPass(document);
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

  // Expose for manual refresh after custom DOM updates
  window.refreshMoneyFormats = function (root) {
    runFormatPass(root || document);
  };
  window.unformatMoneyInputs = unformatMoneyInputs;
})(window, document, window.jQuery);
