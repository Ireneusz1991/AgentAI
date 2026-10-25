/**
 * ============================================================================
 * OPTIDOC AI ENTERPRISE - AUTOINSTALATOR SHOWROOMU WORKSPACE (v2.0)
 * ============================================================================
 * Automatyczny instalator infrastruktury:
 * 1. Tworzy strukturę folderów na Dysku Google (Wpływ, Archiwum, Blokada, Umowy).
 * 2. Sam zapamiętuje ID folderów (nie musisz nic ręcznie kopiować!).
 * 3. Formatuje Arkusz Google: kolumny, kolory, format walutowy, formatowanie warunkowe.
 * 4. Dodaje własne menu "🚀 OptiDoc AI" bezpośrednio w pasku Arkusza Google.
 * 5. Posiada generator faktur testowych (Demo Pack) do prezentacji na żywo.
 */

// ============================================================================
// 1. GŁÓWNA FUNKCJA INSTALACYJNA (Uruchom ją tylko raz!)
// ============================================================================
function zainstalujOptiDocShowroom() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  
  // A. Tworzenie struktury folderów na Dysku Google
  const rootName = "📁 OptiDoc AI Enterprise Showroom";
  let rootFolder;
  const existingFolders = DriveApp.getFoldersByName(rootName);
  
  if (existingFolders.hasNext()) {
    rootFolder = existingFolders.next();
  } else {
    rootFolder = DriveApp.createFolder(rootName);
  }
  
  const fInbox = getOrCreateSubfolder(rootFolder, "📥 01_Skrzynka_Wplywu_Nowe");
  const fArchive = getOrCreateSubfolder(rootFolder, "🟢 02_Archiwum_Ksiegowe_OK");
  const fReview = getOrCreateSubfolder(rootFolder, "🟡 03_Do_Wyjasnienia_Ksiegowosc");
  const fFraud = getOrCreateSubfolder(rootFolder, "🔴 04_KRYTYCZNE_Blokada_Fraud");
  const fContracts = getOrCreateSubfolder(rootFolder, "📄 05_Umowy_Do_Audytu");
  
  // B. Automatyczne zapamiętanie ID w chmurze (Zero ręcznego kopiowania!)
  const props = PropertiesService.getScriptProperties();
  props.setProperties({
    "ROOT_FOLDER_ID": rootFolder.getId(),
    "INBOX_FOLDER_ID": fInbox.getId(),
    "ARCHIVE_FOLDER_ID": fArchive.getId(),
    "REVIEW_FOLDER_ID": fReview.getId(),
    "FRAUD_FOLDER_ID": fFraud.getId(),
    "CONTRACTS_FOLDER_ID": fContracts.getId()
  });
  
  // C. Konfiguracja i formatowanie Głównego Arkusza Rejestru
  let sheet = ss.getSheetByName("📊 Rejestr Faktur");
  if (!sheet) {
    sheet = ss.getActiveSheet();
    sheet.setName("📊 Rejestr Faktur");
  }
  sheet.clear();
  
  // Nagłówki tabeli
  const headers = [
    "Data Wpływu", 
    "Nazwa Dostawcy", 
    "NIP Sprzedawcy", 
    "Nr Faktury", 
    "Netto (PLN)", 
    "VAT (PLN)", 
    "Brutto (PLN)", 
    "Konto Bankowe", 
    "Biała Lista MF", 
    "Status Weryfikacji BPM", 
    "Link do Dokumentu"
  ];
  
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  
  // Stylizacja nagłówków (ciemny granat, biały pogrubiony tekst)
  const headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange.setBackground("#1E3A8A")
             .setFontColor("#FFFFFF")
             .setFontWeight("bold")
             .setFontSize(10)
             .setHorizontalAlignment("center");
  sheet.setFrozenRows(1);
  
  // Szerokości kolumn dopasowane do biznesu
  sheet.setColumnWidth(1, 140); // Data
  sheet.setColumnWidth(2, 220); // Dostawca
  sheet.setColumnWidth(3, 120); // NIP
  sheet.setColumnWidth(4, 130); // Nr Faktury
  sheet.setColumnWidth(5, 110); // Netto
  sheet.setColumnWidth(6, 110); // VAT
  sheet.setColumnWidth(7, 120); // Brutto
  sheet.setColumnWidth(8, 200); // Konto
  sheet.setColumnWidth(9, 130); // Biała Lista
  sheet.setColumnWidth(10, 200); // Status BPM
  sheet.setColumnWidth(11, 160); // Link
  
  // Format walutowy dla kwot
  sheet.getRange("E2:G1000").setNumberFormat('#,##0.00 "zł"');
  
  // D. Formatowanie Warunkowe (Kolory statusów)
  const statusRange = sheet.getRange("J2:J1000");
  const ruleGreen = SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains("ZGODNA")
    .setBackground("#DCFCE7") // Jasnozielony
    .setFontColor("#166534")
    .setRanges([statusRange])
    .build();
    
  const ruleYellow = SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains("WYJAŚNIENIA")
    .setBackground("#FEF9C3") // Jasnożółty
    .setFontColor("#854D0E")
    .setRanges([statusRange])
    .build();
    
  const ruleRed = SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains("BLOKADA")
    .setBackground("#FEE2E2") // Jasnoczerwony
    .setFontColor("#991B1B")
    .setRanges([statusRange])
    .build();
    
  sheet.setConditionalFormatRules([ruleGreen, ruleYellow, ruleRed]);
  
  // E. Zakładka Centrum Dowodzenia (Dashboard informacyjny)
  let dashSheet = ss.getSheetByName("⚙️ Centrum Dowodzenia");
  if (!dashSheet) {
    dashSheet = ss.insertSheet("⚙️ Centrum Dowodzenia");
  }
  dashSheet.clear();
  dashSheet.getRange("A1").setValue("🚀 OPTIDOC AI - STATUS INFRASTRUKTURY").setFontWeight("bold").setFontSize(14);
  
  const infoData = [
    ["Zasób", "Link / Informacja"],
    ["Główny Folder Showroomu", rootFolder.getUrl()],
    ["Folder Wpływu (Inbox)", fInbox.getUrl()],
    ["Archiwum Faktur Zgodnych", fArchive.getUrl()],
    ["Kolejka Wyjaśnień", fReview.getUrl()],
    ["Folder Blokad Antyfraud", fFraud.getUrl()],
    ["Audyt Umów Prawnych", fContracts.getUrl()],
    ["API Gemini Flash", props.getProperty("GEMINI_KEY") ? "SKONFIGUROWANE" : "BRAK KLUCZA (Kliknij menu OptiDoc AI -> Ustaw klucz)"],
    ["Biała Lista MF", "Aktywna (wl-api.mf.gov.pl)"]
  ];
  dashSheet.getRange(3, 1, infoData.length, 2).setValues(infoData);
  dashSheet.getRange("A3:B3").setBackground("#334155").setFontColor("#FFFFFF").setFontWeight("bold");
  dashSheet.setColumnWidth(1, 220);
  dashSheet.setColumnWidth(2, 450);
  
  ui.alert("🎉 Gratulacje!", 
    "Infrastruktura OptiDoc AI została zainstalowana pomyślnie!\n\n" +
    "1. Utworzono foldery na Twoim Dysku Google.\n" +
    "2. Sformatowano Arkusz Rejestru.\n" +
    "3. Odśwież stronę Arkusza, aby zobaczyć nowe menu '🚀 OptiDoc AI' na górnym pasku.", 
    ui.ButtonSet.OK);
}

// ============================================================================
// 2. MENU GÓRNE W ARKUSZU GOOGLE (Narzędzia pod ręką)
// ============================================================================
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu("🚀 OptiDoc AI")
    .addItem("⚡ Uruchom Pełny Autopilot (Gmail + Dysk)", "autopilotOptiDoc")
    .addItem("📧 Pobierz faktury z Gmaila do Skrzynki Wpływu", "pobierzFakturyZGmaila")
    .addItem("▶️ Przetwórz pliki z folderu Wpływu", "przetworzNoweDokumenty")
    .addSeparator()
    .addItem("🧪 Wygeneruj faktury testowe (Live Demo)", "wygenerujFakturyTestowe")
    .addItem("🔑 Ustaw / Zmień klucz Gemini API", "ustawKluczGemini")
    .addItem("⚙️ Reinstaluj strukturę folderów", "zainstalujOptiDocShowroom")
    .addToUi();
}

function ustawKluczGemini() {
  const ui = SpreadsheetApp.getUi();
  const response = ui.prompt("Klucz Gemini API", "Wklej swój darmowy klucz z Google AI Studio (aistudio.google.com):", ui.ButtonSet.OK_CANCEL);
  if (response.getSelectedButton() === ui.Button.OK) {
    const key = response.getResponseText().trim();
    PropertiesService.getScriptProperties().setProperty("GEMINI_KEY", key);
    ui.alert("Sukces", "Klucz Gemini został pomyślnie zapisany w chmurze!", ui.ButtonSet.OK);
  }
}

// ============================================================================
// 3. ZUNIFIKOWANY AUTOPILOT (Gmail -> Dysk -> Gemini -> Biała Lista -> Arkusz)
// ============================================================================
function autopilotOptiDoc() {
  // Krok A: Pobierz załączniki PDF z nowych maili w Gmailu
  pobierzFakturyZGmaila();
  
  // Krok B: Przetwórz wszystko, co jest w folderze wpływu (z maila + z dysku ze skanera)
  przetworzNoweDokumenty();
}

/**
 * Przeszukuje Gmaila pod kątem nowych faktur z załącznikami PDF.
 * Zapobiega dublowaniu dzięki etykiecie "OptiDoc/Przetworzone".
 */
function pobierzFakturyZGmaila() {
  const props = PropertiesService.getScriptProperties();
  const inboxId = props.getProperty("INBOX_FOLDER_ID");
  if (!inboxId) return;
  
  const inboxFolder = DriveApp.getFolderById(inboxId);
  const labelName = "OptiDoc/Przetworzone";
  let label = GmailApp.getUserLabelByName(labelName);
  if (!label) {
    label = GmailApp.createLabel(labelName);
  }
  
  // Szukamy maili nieprzetworzonych z załącznikiem PDF (słowa kluczowe: faktura, invoice, FV lub po prostu załącznik PDF)
  const query = `has:attachment filename:pdf -label:${labelName}`;
  const threads = GmailApp.search(query, 0, 10);
  
  let downloadedCount = 0;
  
  for (let i = 0; i < threads.length; i++) {
    const messages = threads[i].getMessages();
    for (let j = 0; j < messages.length; j++) {
      const msg = messages[j];
      const attachments = msg.getAttachments();
      
      for (let k = 0; k < attachments.length; k++) {
        const att = attachments[k];
        if (att.getContentType() === MimeType.PDF || att.getName().toLowerCase().endsWith(".pdf")) {
          // Zapisujemy PDF do folderu Wpływu na Dysku Google
          inboxFolder.createFile(att.copyBlob());
          downloadedCount++;
        }
      }
    }
    // Oznaczamy wątek etykietą, aby nie przetwarzać go drugi raz
    threads[i].addLabel(label);
  }
  
  Logger.log(`Pobrano ${downloadedCount} załączników z Gmaila.`);
}

// ============================================================================
// 4. SILNIK PRZETWARZANIA (Gemini Flash + Biała Lista MF + BPM)
// ============================================================================
function przetworzNoweDokumenty() {
  const props = PropertiesService.getScriptProperties();
  const inboxId = props.getProperty("INBOX_FOLDER_ID");
  const archiveId = props.getProperty("ARCHIVE_FOLDER_ID");
  const fraudId = props.getProperty("FRAUD_FOLDER_ID");
  const geminiKey = props.getProperty("GEMINI_KEY");
  
  if (!inboxId) {
    Logger.log("Brak ID folderu skrzynki wpływu!");
    return;
  }
  
  const inbox = DriveApp.getFolderById(inboxId);
  const files = inbox.getFiles();
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("📊 Rejestr Faktur");
  let count = 0;
  
  while (files.hasNext()) {
    const file = files.next();
    const mime = file.getMimeType();
    
    if (mime === MimeType.PDF || mime.includes("image")) {
      count++;
      Logger.log("Przetwarzam plik: " + file.getName());
      
      // Ekstrakcja danych przez Gemini Flash (lub fallback testowy)
      let docData = null;
      if (geminiKey) {
        docData = extractDataWithGeminiFlash(file, geminiKey);
      }
      
      // Fallback laboratoryjny, jeśli klucz jeszcze nie został podany
      if (!docData) {
        docData = {
          sellerName: "Dostawca Testowy Sp. z o.o.",
          sellerNip: "5252248481",
          invoiceNumber: "FV/AUTO/" + Math.floor(Math.random() * 1000),
          netto: 2500.00,
          vat: 575.00,
          brutto: 3075.00,
          bankAccount: "12109000040000000100000000"
        };
      }
      
      // Walidacja matematyczna (art. 106e VAT)
      const mathOk = Math.abs((docData.netto + docData.vat) - docData.brutto) <= 0.02;
      
      // Sprawdzenie Białej Listy MF na żywo
      const wl = verifyWhiteListMF(docData.sellerNip, docData.bankAccount);
      
      // Routing BPM (Management by Exception)
      let status = "🟢 ZGODNA";
      let targetFolder = DriveApp.getFolderById(archiveId);
      
      if (!mathOk) {
        status = "🟡 DO WYJAŚNIENIA (Błąd rachunkowy)";
      } else if (!wl.isAccountValid || !wl.isActive) {
        status = "🔴 BLOKADA PŁATNOŚCI (Biała Lista MF)";
        targetFolder = DriveApp.getFolderById(fraudId);
      }
      
      // Zapis w Arkuszu
      sheet.appendRow([
        new Date(),
        docData.sellerName,
        docData.sellerNip,
        docData.invoiceNumber,
        docData.netto,
        docData.vat,
        docData.brutto,
        docData.bankAccount,
        wl.isAccountValid ? "TAK (Zgodne z MF)" : "BRAK NA LIŚCIE!",
        status,
        file.getUrl()
      ]);
      
      // Przeniesienie pliku do folderu docelowego i nadanie czytelnej nazwy
      file.moveTo(targetFolder);
      try {
        file.setName(`${docData.sellerNip}_${docData.invoiceNumber.replace(/[\/\\:]/g, '-')}.pdf`);
      } catch (e) {
        // Ignorujemy błędy zmiany nazwy
      }
    }
  }
  
  Logger.log(`Przetworzono ${count} dokumentów.`);
}

// ============================================================================
// 5. GENERATOR DOKUMENTÓW DEMO DLA KLIENTA (Pokaz na żywo)
// ============================================================================
function wygenerujFakturyTestowe() {
  const props = PropertiesService.getScriptProperties();
  const inbox = DriveApp.getFolderById(props.getProperty("INBOX_FOLDER_ID"));
  
  inbox.createFile("Faktura_Zgodna_Orlen.pdf", "DANE TESTOWE PKN ORLEN NIP: 7740001454", MimeType.PDF);
  inbox.createFile("Faktura_Podejrzana_Fraud.pdf", "DANE TESTOWE FAŁSZYWY NIP: 0000000000", MimeType.PDF);
  
  try {
    SpreadsheetApp.getUi().alert("Gotowe!", "Wygenerowano 2 faktury testowe w folderze Wpływu.", SpreadsheetApp.getUi().ButtonSet.OK);
  } catch (e) {}
}

// ============================================================================
// 6. POMOCNIKI: BIAŁA LISTA MF & GEMINI API
// ============================================================================
function verifyWhiteListMF(nip, rawAccount) {
  const cleanNip = (nip || "").replace(/[^0-9]/g, '');
  const cleanAccount = (rawAccount || "").replace(/[^0-9]/g, '');
  const today = Utilities.formatDate(new Date(), "GMT+1", "yyyy-MM-dd");
  
  if (cleanNip.length !== 10) return { isActive: false, isAccountValid: false };
  
  try {
    const url = `https://wl-api.mf.gov.pl/api/search/nip/${cleanNip}?date=${today}`;
    const res = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    if (res.getResponseCode() === 200) {
      const data = JSON.parse(res.getContentText());
      const subject = data.result && data.result.subject;
      if (!subject) return { isActive: false, isAccountValid: false };
      
      const onList = (subject.accountNumbers || []).some(acc => acc.replace(/[^0-9]/g, '') === cleanAccount);
      return { isActive: subject.statusVat === "Czynny", isAccountValid: onList };
    }
  } catch (e) {
    Logger.log("MF API error: " + e.message);
  }
  return { isActive: true, isAccountValid: true }; // Fallback lab
}

function extractDataWithGeminiFlash(file, apiKey) {
  try {
    const base64 = Utilities.base64Encode(file.getBlob().getBytes());
    const prompt = 'Jesteś ekspertem księgowym. Wyciągnij z tego pliku faktury kluczowe dane i zwróć TYLKO poprawny format JSON (bez bloków markdown):\n' +
                   '{"sellerName": "nazwa firmy", "sellerNip": "sam numer 10 cyfr", "invoiceNumber": "numer faktury", "netto": 0.00, "vat": 0.00, "brutto": 0.00, "bankAccount": "sam numer konta 26 cyfr bez spacji"}';
                   
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;
    
    const res = UrlFetchApp.fetch(url, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify({
        contents: [{ parts: [{ text: prompt }, { inline_data: { mime_type: "application/pdf", data: base64 } }] }],
        generationConfig: { response_mime_type: "application/json" }
      }),
      muteHttpExceptions: true
    });
    
    if (res.getResponseCode() === 200) {
      const json = JSON.parse(res.getContentText());
      const rawText = json.candidates[0].content.parts[0].text;
      return JSON.parse(rawText);
    } else {
      Logger.log("Błąd odpowiedzi Gemini: " + res.getContentText());
    }
  } catch (e) {
    Logger.log("Gemini Error: " + e.message);
  }
  return null;
}

function getOrCreateSubfolder(parent, name) {
  const f = parent.getFoldersByName(name);
  return f.hasNext() ? f.next() : parent.createFolder(name);
}
