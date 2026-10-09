/**
 * Afrikbook money helpers
 *
 * Display: thousand separators on money (1,234.56)
 * Math:    parseMoney always strips commas
 * Submit:  commas stripped so the DB stores plain numbers
 */
(function (window, document, $) {
  "use strict";

  var MONEY_HEADER_RE =
    /amount|price|total|cost|paid|expected|outstanding|balance|sales|purchase|salary|discount|vat|fee|charge|credit|debit/i;

  var SKIP_HEADER_RE = /\b(qty|quantity|sn|s\/n|date|ids?|name|code|item|desc|type|status)\b/i;

  var QTY_RE = /^(qty\[\]|qty|quantity|line_qty\[\]|new_qty\[\]|duration|months|days|limit|usage)$/i;

  var MONEY_NAME_RE =
    /(amount|price|total|cost|paid|expected|outstanding|balance|salary|discount|vat|fee|charge|credit|debit|^dbt(\[\])?$|^cr(\[\])?$|transfer|cash|^pos$|unit(\[\])?$|part_payment|payment_amount|borrowed|interest|wholesale|retailer|selling|sub-total|sub_total)/i;

  var SKIP_NAME_RE =
    /(qty|quantity|date|phone|email|code|invoice|item|desc|password|user|page|duration|month|day|year|limit|usage|account_id|customer_id|vendor_id)/i;

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

  function unformatString(value) {
    var n = parseMoney(value);
    return n.toFixed(2);
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

  function fieldKey(el) {
    return String((el && (el.name || el.id)) || "");
  }

  function isQtyField(el) {
    if (!el) return false;
    var key = fieldKey(el);
    if (QTY_RE.test(key)) return true;
    if (/(^|_)qty(\[\]|_|$)/i.test(key) || /quantity/i.test(key)) return true;
    return false;
  }

  function isMoneyInput(el) {
    if (!el || !/^(INPUT|TEXTAREA)$/i.test(el.tagName)) return false;
    if (isQtyField(el)) return false;
    var type = (el.type || "text").toLowerCase();
    if (/checkbox|radio|file|date|time|email|password|button|submit|hidden|search|tel|url|color/.test(type)) {
      return false;
    }
    if (el.getAttribute("data-money-skip") === "1") return false;
    if (el.classList && el.classList.contains("money-input")) return true;
    if (el.getAttribute("data-money") === "1") return true;
    if (el.getAttribute("data-money-display") === "1") return true;
    if (el.getAttribute("data-money-format") === "1") return true;
    var key = fieldKey(el);
    if (!key) return false;
    if (SKIP_NAME_RE.test(key) && !MONEY_NAME_RE.test(key)) return false;
    return MONEY_NAME_RE.test(key);
  }

  function enableCommaInput(el) {
    if (!el || el.tagName !== "INPUT") return;
    if (el.type === "number" && isMoneyInput(el)) {
      try {
        el.type = "text";
        el.setAttribute("inputmode", "decimal");
        el.setAttribute("data-money-was-number", "1");
      } catch (err) {}
    }
  }

  function formatInput(el) {
    if (!el || el.value === undefined || el.value === null) return;
    if (el === document.activeElement) return;
    if (String(el.value).trim() === "") return;
    if (!looksLikePlainNumber(el.value)) return;
    enableCommaInput(el);
    el.value = formatMoney(el.value);
  }

  function unformatInput(el) {
    if (!el || el.value === undefined || el.value === null) return;
    if (String(el.value).indexOf(",") === -1 && !/[₦$£€]/.test(String(el.value))) return;
    if (!looksLikePlainNumber(el.value)) return;
    el.value = unformatString(el.value);
  }

  function setMoneyValue(el, n) {
    if (!el) return;
    if (el.jquery) el = el[0];
    if (!el) return;
    if (n === "" || n === null || n === undefined) {
      el.value = "";
      return;
    }
    enableCommaInput(el);
    if (el === document.activeElement) {
      el.value = unformatString(n);
    } else {
      el.value = formatMoney(n);
    }
  }

  window.setMoneyValue = setMoneyValue;

  function formatElementText(el) {
    if (!el || el.getAttribute("data-money-skip") === "1") return;
    if (/^(INPUT|SELECT|TEXTAREA)$/i.test(el.tagName)) return;
    if (el.querySelector && el.querySelector("input, select, textarea, a, button, svg")) return;
    var text = (el.textContent || "").trim();
    if (!looksLikePlainNumber(text)) return;
    var formatted = formatMoney(text);
    if (el.textContent !== formatted) {
      el.textContent = formatted;
    }
    el.setAttribute("data-money-formatted", "1");
  }

  function formatMoneyClassTargets(root) {
    root = root || document;
    var nodes = root.querySelectorAll(".money, .money-value, [data-money], .currency-amount");
    nodes.forEach(function (el) {
      if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
        formatInput(el);
        return;
      }
      formatElementText(el);
    });
  }

  function moneyColumnIndexes(table) {
    var indexes = [];
    var headers = table.querySelectorAll("thead th, thead td");
    headers.forEach(function (th, idx) {
      var label = (th.textContent || "").trim();
      if (MONEY_HEADER_RE.test(label) && !SKIP_HEADER_RE.test(label)) {
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
      var cols = moneyColumnIndexes(table);
      if (!cols.length) return;
      var rows = table.querySelectorAll("tbody tr, tfoot tr");
      rows.forEach(function (tr) {
        cols.forEach(function (colIdx) {
          var cell = tr.children[colIdx];
          if (!cell) return;
          if (cell.querySelector && cell.querySelector("input, select, textarea, a, button, svg")) return;
          formatElementText(cell);
        });
      });
    });
  }

  function unformatMoneyInputs(form) {
    var scope = form || document;
    var fields = scope.querySelectorAll("input, textarea");
    fields.forEach(function (el) {
      if (!el.value || String(el.value).indexOf(",") === -1) return;
      if (looksLikePlainNumber(el.value)) {
        el.value = unformatString(el.value);
      }
    });
  }

  function bindMoneyInputUX(root) {
    root = root || document;
    var fields = root.querySelectorAll("input, textarea");
    fields.forEach(function (el) {
      if (!isMoneyInput(el) && el.getAttribute("data-money-format") !== "1") return;
      enableCommaInput(el);
      if (el.getAttribute("data-money-bound") === "1") return;
      el.setAttribute("data-money-bound", "1");

      el.addEventListener("focus", function () {
        if (el.value && looksLikePlainNumber(el.value)) {
          el.value = unformatString(el.value);
        }
      });

      el.addEventListener("blur", function () {
        formatInput(el);
      });

      el.addEventListener("input", function () {
        var cleaned = String(el.value).replace(/[^\d.,\-]/g, "");
        if (cleaned !== el.value) el.value = cleaned;
      });

      if (el.value && el !== document.activeElement) {
        formatInput(el);
      }
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
                return "=" + encodeURIComponent(unformatString(decoded));
              }
            } catch (err) {}
            return m;
          });
        } else if (typeof options.data === "object" && !(options.data instanceof FormData)) {
          Object.keys(options.data).forEach(function (k) {
            var v = options.data[k];
            if (typeof v === "string" && v.indexOf(",") !== -1 && looksLikePlainNumber(v)) {
              options.data[k] = unformatString(v);
            }
          });
        }
      });
    }
  }

  function patchJQueryVal() {
    if (!$ || !$.fn || $.fn.val && $.fn.val._afrikbookMoney) return;
    var origVal = $.fn.val;
    $.fn.val = function (value) {
      if (arguments.length === 0) {
        var raw = origVal.call(this);
        if (this.length === 1 && isMoneyInput(this[0]) && looksLikePlainNumber(raw)) {
          return unformatString(raw);
        }
        return raw;
      }
      if (typeof value === "function" || Array.isArray(value)) {
        return origVal.apply(this, arguments);
      }
      this.each(function () {
        var v = value;
        if (isMoneyInput(this) && v !== undefined && v !== null && v !== "") {
          enableCommaInput(this);
          if (looksLikePlainNumber(String(v))) {
            v = this === document.activeElement ? unformatString(v) : formatMoney(v);
          }
        }
        origVal.call($(this), v);
      });
      return this;
    };
    $.fn.val._afrikbookMoney = true;
  }

  function runFormatPass(root) {
    try {
      bindMoneyInputUX(root);
      formatMoneyClassTargets(root);
      formatTableMoneyColumns(root);
    } catch (e) {
      if (window.console && console.warn) console.warn("[money.js]", e);
    }
  }

  function init() {
    patchJQueryVal();
    bindFormSubmitSanitize();
    runFormatPass(document);

    if ($ && $(document).ajaxComplete) {
      $(document).ajaxComplete(function () {
        setTimeout(function () {
          runFormatPass(document);
        }, 30);
      });
    }

    if (window.MutationObserver && document.body) {
      var obs = new MutationObserver(function (mutations) {
        var need = false;
        mutations.forEach(function (m) {
          if (m.addedNodes && m.addedNodes.length) need = true;
        });
        if (need) {
          clearTimeout(window.__moneyFmtTimer);
          window.__moneyFmtTimer = setTimeout(function () {
            runFormatPass(document);
          }, 60);
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
})(window, document, window.jQuery);
