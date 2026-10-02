/**
 * Robim Good — данные для страницы «Где купить в банке» (версия 2).
 *
 * Таблица остаётся ЗАКРЫТОЙ: её не нужно публиковать. Страница получает точки через это
 * веб-приложение, и наружу уходят только поля, нужные для карты: название, тип, город,
 * адрес, телефон, координаты, «Точка» и сорта. Заметки менеджера, статусы проверки и
 * другие листы не видны никому.
 *
 * Что делает скрипт:
 *   — сам находит координаты по адресу (Google Карты), когда адрес добавлен или изменён;
 *   — проверяет каждую строку и пишет результат в колонку status; строки с ошибкой
 *     подсвечиваются и НЕ попадают на сайт;
 *   — раз в день обновляет рейтинги Untappd на листе «untappd».
 *
 * Установка (один раз, под аккаунтом пивоварни — владельцем таблицы):
 *   1. Расширения → Apps Script. Вставьте этот файл вместо содержимого Code.gs, сохраните.
 *   2. Выберите функцию install → «Выполнить» → разрешите доступ.
 *      Появятся меню «Robim Good», проверка при каждой правке и обновление рейтингов.
 *   3. «Развернуть» → «Новое развёртывание» → тип «Веб-приложение»:
 *        Выполнять от имени: «Я»;  У кого есть доступ: «Все».
 *      Скопируйте ссылку …/exec и вставьте её в блок на Tilda, в строку dataUrl: '…'.
 *   После изменения этого кода: «Развернуть» → «Управление развёртываниями» → изменить →
 *   «Новая версия». Ссылка при этом не меняется.
 */

var SHEET_POINTS = 'Точки';
var SHEET_UNTAPPD = 'untappd';
var COLS = ['city', 'name', 'type', 'address', 'phone', 'tochka', 'sorts', 'lat', 'lng', 'status', 'notes'];
var HEADERS = ['Город', 'Название', 'Тип', 'Адрес', 'Телефон', 'Сеть «Точка»', 'Сорта (через запятую)', 'Широта', 'Долгота', 'Проверка', 'Заметки (не видны на сайте)'];
var TYPES = ['Магазин', 'Бар', 'Магазин-бар'];
var BELARUS = { latMin: 51.2, latMax: 56.2, lngMin: 23.1, lngMax: 32.8 };
var PUBLIC_FIELDS = ['city', 'name', 'type', 'address', 'phone', 'tochka', 'sorts', 'lat', 'lng'];
var CACHE_KEY = 'site-json';

/* ===================== Установка и меню ===================== */

function install() {
  var ss = SpreadsheetApp.getActive();
  ScriptApp.getProjectTriggers().forEach(function (t) { ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('onEditInstalled').forSpreadsheet(ss).onEdit().create();
  ScriptApp.newTrigger('checkAllPoints').timeBased().everyHours(1).create();
  ScriptApp.newTrigger('updateUntappd').timeBased().everyDays(1).atHour(6).create();
  setupPointsSheet_();
  checkAllPoints();
  updateUntappd();
}

function onOpen() {
  SpreadsheetApp.getUi().createMenu('Robim Good')
    .addItem('Проверить все точки', 'checkAllPoints')
    .addItem('Обновить рейтинги Untappd', 'updateUntappd')
    .addToUi();
}

function setupPointsSheet_() {
  var ss = SpreadsheetApp.getActive();
  var sh = ss.getSheetByName(SHEET_POINTS) || ss.insertSheet(SHEET_POINTS, 0);
  sh.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]).setFontWeight('bold').setBackground('#10202e').setFontColor('#ffffff');
  sh.setFrozenRows(1);
  var rows = Math.max(sh.getMaxRows() - 1, 500);
  var col = function (name) { return COLS.indexOf(name) + 1; };
  sh.getRange(2, col('type'), rows).setDataValidation(
    SpreadsheetApp.newDataValidation().requireValueInList(TYPES, true).setAllowInvalid(false).build());
  sh.getRange(2, col('tochka'), rows).setDataValidation(
    SpreadsheetApp.newDataValidation().requireValueInList(['да', ''], true).setAllowInvalid(false).build());
  sh.getRange(2, col('status'), rows).setFontColor('#4a5a6a');
  // Шапку можно менять только владельцу: так колонки не переименуют случайно.
  sh.getProtections(SpreadsheetApp.ProtectionType.RANGE).forEach(function (p) { p.remove(); });
  var protection = sh.getRange(1, 1, 1, HEADERS.length).protect().setDescription('Шапка таблицы точек');
  protection.removeEditors(protection.getEditors());
  if (protection.canDomainEdit()) protection.setDomainEdit(false);
}

/* ===================== Проверка и координаты ===================== */

function onEditInstalled(e) {
  var sh = e.range.getSheet();
  if (sh.getName() !== SHEET_POINTS || e.range.getRow() < 2) return;
  var first = e.range.getRow(), last = e.range.getLastRow();
  var c1 = e.range.getColumn(), c2 = e.range.getLastColumn();
  var addrChanged = [COLS.indexOf('city') + 1, COLS.indexOf('address') + 1].some(function (c) { return c >= c1 && c <= c2; });
  if (addrChanged) {
    // Адрес изменился — старые координаты больше не верны, найдём заново.
    sh.getRange(first, COLS.indexOf('lat') + 1, last - first + 1, 2).clearContent();
  }
  checkRows_(sh, first, last);
}

function checkAllPoints() {
  var sh = SpreadsheetApp.getActive().getSheetByName(SHEET_POINTS);
  if (sh && sh.getLastRow() > 1) checkRows_(sh, 2, sh.getLastRow());
}

function checkRows_(sh, first, last) {
  var n = last - first + 1;
  var range = sh.getRange(first, 1, n, COLS.length);
  var values = range.getValues();
  var colors = [];
  var geocoder = Maps.newGeocoder().setRegion('by').setLanguage('ru');

  values.forEach(function (v) {
    var r = toRow_(v);
    var empty = !String(r.city).trim() && !String(r.address).trim() && !String(r.name).trim();
    if (empty) { v[COLS.indexOf('status')] = ''; colors.push(null); return; }

    if ((r.lat === '' || r.lng === '') && r.city && r.address) {
      var hit = geocode_(geocoder, r.city, r.address);
      if (hit) { r.lat = hit.lat; r.lng = hit.lng; }
    }
    var problems = problems_(r);
    v[COLS.indexOf('lat')] = r.lat;
    v[COLS.indexOf('lng')] = r.lng;
    v[COLS.indexOf('status')] = problems.length ? 'Ошибка: ' + problems.join('; ') : 'ok';
    colors.push(problems.length ? '#fde2dc' : null);
  });

  range.setValues(values);
  range.setBackgrounds(colors.map(function (c) { return COLS.map(function () { return c; }); }));
  CacheService.getScriptCache().remove(CACHE_KEY);
}

function geocode_(geocoder, city, address) {
  try {
    var res = geocoder.geocode(city + ', ' + address + ', Беларусь');
    var best = (res.results || [])[0];
    if (!best) return null;
    var loc = best.geometry.location;
    if (!inBelarus_(loc.lat, loc.lng)) return null;
    return { lat: Math.round(loc.lat * 1e6) / 1e6, lng: Math.round(loc.lng * 1e6) / 1e6 };
  } catch (err) {
    console.warn('geocode ' + city + ', ' + address + ': ' + err);
    return null;
  }
}

function problems_(r) {
  var p = [];
  if (!String(r.city).trim()) p.push('нет города');
  if (!String(r.address).trim()) p.push('нет адреса');
  if (!String(r.name).trim()) p.push('нет названия');
  if (TYPES.indexOf(r.type) < 0) p.push('тип: выберите из списка');
  var digits = String(r.phone).replace(/\D/g, '');
  if (r.phone !== '' && (digits.length < 9 || digits.length > 12)) p.push('телефон не похож на номер');
  if (r.lat === '' || r.lng === '') p.push('адрес не найден на карте: проверьте его или впишите координаты');
  else if (!inBelarus_(Number(r.lat), Number(r.lng))) p.push('координаты вне Беларуси');
  return p;
}

function inBelarus_(lat, lng) {
  return lat >= BELARUS.latMin && lat <= BELARUS.latMax && lng >= BELARUS.lngMin && lng <= BELARUS.lngMax;
}

function toRow_(values) {
  var r = {};
  COLS.forEach(function (c, i) { r[c] = typeof values[i] === 'string' ? values[i].trim() : values[i]; });
  return r;
}

/* ===================== Веб-приложение для сайта ===================== */

function doGet() {
  var cache = CacheService.getScriptCache();
  var json = cache.get(CACHE_KEY);
  if (!json) {
    json = JSON.stringify({ updated: new Date().toISOString(), points: sitePoints_(), untappd: untappdRows_() });
    if (json.length < 90000) cache.put(CACHE_KEY, json, 300); // 5 минут
  }
  return ContentService.createTextOutput(json).setMimeType(ContentService.MimeType.JSON);
}

function sitePoints_() {
  var sh = SpreadsheetApp.getActive().getSheetByName(SHEET_POINTS);
  if (!sh || sh.getLastRow() < 2) return [];
  return sh.getRange(2, 1, sh.getLastRow() - 1, COLS.length).getValues().map(toRow_)
    .filter(function (r) { return r.status === 'ok'; }) // на сайт — только проверенные строки
    .map(function (r) {
      var out = {};
      PUBLIC_FIELDS.forEach(function (f) { out[f] = r[f]; });
      out.tochka = String(r.tochka).toLowerCase() === 'да';
      out.sorts = String(r.sorts || '').split(/[,;]/).map(function (s) { return s.trim(); }).filter(String);
      out.phone = String(r.phone || '').replace(/[^\d+]/g, '');
      return out;
    });
}

/* ===================== Рейтинги Untappd ===================== */

var UNTAPPD_FIELDS = ['key', 'beer', 'url', 'rating', 'ratings', 'updated', 'quote', 'quote_author'];
var UNTAPPD_DEFAULTS = [
  ['brewery', 'Robim Good Brewery', 'https://untappd.com/Robim_Good_Brewery'],
  ['vista', 'FACTORY I.P.A Vista', 'https://untappd.com/b/robim-good-brewery-factory-ipa-vista/6753498'],
  ['bbq', 'FACTORY TOMATO BBQ', 'https://untappd.com/b/robim-good-brewery-bbq-tomato-beer/6798506'],
  ['zipa', 'Zero IPA', 'https://untappd.com/b/robim-good-brewery-robim-good-zero-ipa/6772342'],
  ['zlager', 'Zero Lager', 'https://untappd.com/b/robim-good-brewery-robim-good-zero/6772340']
];

function updateUntappd() {
  var ss = SpreadsheetApp.getActive();
  var sheet = ss.getSheetByName(SHEET_UNTAPPD) || ss.insertSheet(SHEET_UNTAPPD);
  var rows = untappdRows_();
  if (!rows.length) rows = UNTAPPD_DEFAULTS.map(function (d) { return { key: d[0], beer: d[1], url: d[2] }; });

  rows.forEach(function (row) {
    if (!row.url) return;
    try {
      var res = UrlFetchApp.fetch(row.url, { muteHttpExceptions: true, headers: { 'User-Agent': 'Mozilla/5.0 (compatible; RobimGoodRatings/1.0; +https://robimgood.beer)' } });
      var m = res.getContentText().match(/"aggregateRating":\{[^}]*?"ratingValue":([\d.]+)[^}]*?"reviewCount":(\d+)/);
      if (res.getResponseCode() === 200 && m) {
        row.rating = Math.round(parseFloat(m[1]) * 1000) / 1000;
        row.ratings = parseInt(m[2], 10);
        row.updated = Utilities.formatDate(new Date(), ss.getSpreadsheetTimeZone(), 'yyyy-MM-dd');
      }
    } catch (e) { console.warn(row.url + ': ' + e); }
    Utilities.sleep(1500);
  });

  sheet.clearContents();
  sheet.getRange(1, UNTAPPD_FIELDS.indexOf('updated') + 1, rows.length + 1, 1).setNumberFormat('@');
  sheet.getRange(1, 1, rows.length + 1, UNTAPPD_FIELDS.length).setValues(
    [UNTAPPD_FIELDS].concat(rows.map(function (r) { return UNTAPPD_FIELDS.map(function (f) { return r[f] === undefined ? '' : r[f]; }); })));
  CacheService.getScriptCache().remove(CACHE_KEY);
}

function untappdRows_() {
  var sh = SpreadsheetApp.getActive().getSheetByName(SHEET_UNTAPPD);
  if (!sh || sh.getLastRow() < 2) return [];
  return sh.getRange(2, 1, sh.getLastRow() - 1, UNTAPPD_FIELDS.length).getValues().map(function (v) {
    var r = {}; UNTAPPD_FIELDS.forEach(function (f, i) { r[f] = v[i]; }); return r;
  }).filter(function (r) { return r.key; });
}
