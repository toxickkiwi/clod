/**
 * Robim Good — рейтинги Untappd для страницы «Где купить в банке».
 *
 * Раз в день забирает рейтинг и число оценок со страниц Untappd и пишет их
 * на лист «untappd» этой Google-таблицы. Страница читает этот лист как CSV.
 *
 * Установка (один раз):
 *   1. В Google-таблице с точками: Расширения → Apps Script.
 *   2. Вставьте этот файл целиком вместо содержимого Code.gs и сохраните.
 *   3. Вверху выберите функцию install и нажмите «Выполнить», разрешите доступ.
 *      Появится лист «untappd» с рейтингами, а обновление будет идти каждый день в 6:00.
 *
 * Что можно менять прямо на листе «untappd»:
 *   beer          — название, как его видит покупатель;
 *   url           — страница сорта на Untappd (если сменилась карточка сорта);
 *   quote, quote_author — короткий отзыв покупателя (только с разрешения автора).
 * Колонки rating, ratings и updated скрипт перезаписывает сам.
 */

var SHEET = 'untappd';
var FIELDS = ['key', 'beer', 'url', 'rating', 'ratings', 'updated', 'quote', 'quote_author'];
var DEFAULTS = [
  ['brewery', 'Robim Good Brewery', 'https://untappd.com/Robim_Good_Brewery'],
  ['vista', 'FACTORY I.P.A Vista', 'https://untappd.com/b/robim-good-brewery-factory-ipa-vista/6753498'],
  ['bbq', 'FACTORY TOMATO BBQ', 'https://untappd.com/b/robim-good-brewery-bbq-tomato-beer/6798506'],
  ['zipa', 'Zero IPA', 'https://untappd.com/b/robim-good-brewery-robim-good-zero-ipa/6772342'],
  ['zlager', 'Zero Lager', 'https://untappd.com/b/robim-good-brewery-robim-good-zero/6772340']
];

function install() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'updateUntappd') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('updateUntappd').timeBased().everyDays(1).atHour(6).create();
  updateUntappd();
}

function updateUntappd() {
  var ss = SpreadsheetApp.getActive();
  var sheet = ss.getSheetByName(SHEET) || ss.insertSheet(SHEET);
  var values = sheet.getDataRange().getValues();
  var rows = values.length > 1 ? values.slice(1).map(toRow) : DEFAULTS.map(function (d) {
    return { key: d[0], beer: d[1], url: d[2], rating: '', ratings: '', updated: '', quote: '', quote_author: '' };
  });

  rows.forEach(function (row) {
    if (!row.url) return;
    try {
      var res = UrlFetchApp.fetch(row.url, {
        muteHttpExceptions: true,
        headers: { 'User-Agent': 'Mozilla/5.0 (compatible; RobimGoodRatings/1.0; +https://robimgood.beer)' }
      });
      var m = res.getContentText().match(/"aggregateRating":\{[^}]*?"ratingValue":([\d.]+)[^}]*?"reviewCount":(\d+)/);
      if (res.getResponseCode() === 200 && m) {
        row.rating = Math.round(parseFloat(m[1]) * 1000) / 1000;
        row.ratings = parseInt(m[2], 10);
        row.updated = Utilities.formatDate(new Date(), ss.getSpreadsheetTimeZone(), 'yyyy-MM-dd');
      }
      // Иначе оставляем прошлые значения: страница покажет последний известный рейтинг.
    } catch (e) {
      console.warn(row.url + ': ' + e);
    }
    Utilities.sleep(1500);
  });

  sheet.clearContents();
  // Даты храним текстом (2026-10-02), иначе таблица переведёт их в свой формат.
  sheet.getRange(1, FIELDS.indexOf('updated') + 1, rows.length + 1, 1).setNumberFormat('@');
  sheet.getRange(1, 1, rows.length + 1, FIELDS.length).setValues(
    [FIELDS].concat(rows.map(function (r) { return FIELDS.map(function (f) { return r[f] === undefined ? '' : r[f]; }); }))
  );
}

function toRow(values) {
  var row = {};
  FIELDS.forEach(function (f, i) { row[f] = values[i]; });
  return row;
}
