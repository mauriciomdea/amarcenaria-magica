(function () {
  "use strict";

  const CONSENT_KEY = "amm_consent_v1";
  const CONSENT_VERSION = "1.0";
  const consentPanel = document.getElementById("consentPanel");
  const consentCustomize = document.getElementById("consentCustomize");
  const analyticsToggle = document.getElementById("analyticsConsent");
  const ga4Id = document.body.dataset.ga4Id || "";
  let currentConsent = readConsent();
  let consentReturnFocus = null;

  function readConsent() {
    try {
      const stored = JSON.parse(localStorage.getItem(CONSENT_KEY));
      return stored && stored.version === CONSENT_VERSION ? stored : null;
    } catch (_error) {
      return null;
    }
  }

  function writeConsent(analytics) {
    const previousAnalytics = Boolean(currentConsent && currentConsent.analytics);
    currentConsent = {
      version: CONSENT_VERSION,
      necessary: true,
      analytics: Boolean(analytics),
      updatedAt: new Date().toISOString()
    };
    localStorage.setItem(CONSENT_KEY, JSON.stringify(currentConsent));

    if (currentConsent.analytics) {
      enableAnalytics();
    } else if (previousAnalytics) {
      disableAnalytics();
    }
    closeConsent();
  }

  function enableAnalytics() {
    if (!ga4Id || document.querySelector("script[data-amm-ga4]")) return;

    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag("consent", "default", {
      analytics_storage: "denied",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied",
      wait_for_update: 500
    });
    window.gtag("consent", "update", {
      analytics_storage: "granted",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied"
    });
    window.gtag("js", new Date());
    window.gtag("config", ga4Id, { anonymize_ip: true });

    const script = document.createElement("script");
    script.async = true;
    script.dataset.ammGa4 = "true";
    script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(ga4Id);
    document.head.appendChild(script);
  }

  function disableAnalytics() {
    if (typeof window.gtag === "function") {
      window.gtag("consent", "update", {
        analytics_storage: "denied",
        ad_storage: "denied",
        ad_user_data: "denied",
        ad_personalization: "denied"
      });
    }
    document.cookie.split(";").forEach(function (cookie) {
      const name = cookie.split("=")[0].trim();
      if (name === "_ga" || name.indexOf("_ga_") === 0) {
        document.cookie = name + "=; Max-Age=0; path=/; SameSite=Lax";
      }
    });
  }

  function openConsent(customize) {
    if (!consentPanel) return;
    consentReturnFocus = document.activeElement;
    consentPanel.hidden = false;
    if (analyticsToggle) analyticsToggle.checked = Boolean(currentConsent && currentConsent.analytics);
    setCustomize(Boolean(customize));
    window.setTimeout(function () {
      consentPanel.focus({ preventScroll: true });
    }, 0);
  }

  function closeConsent() {
    if (!consentPanel) return;
    consentPanel.hidden = true;
    if (consentReturnFocus && typeof consentReturnFocus.focus === "function") consentReturnFocus.focus();
  }

  function setCustomize(open) {
    if (!consentCustomize) return;
    consentCustomize.hidden = !open;
    consentPanel.querySelectorAll('[data-consent="accept"], [data-consent="reject"], [data-consent="customize"]').forEach(function (button) {
      button.hidden = open;
    });
    const save = consentPanel.querySelector('[data-consent="save"]');
    if (save) save.hidden = !open;
  }

  window.ammTrack = function (eventName, parameters) {
    if (!currentConsent || !currentConsent.analytics || typeof window.gtag !== "function") return;
    window.gtag("event", eventName, parameters || {});
  };

  if (currentConsent && currentConsent.analytics) enableAnalytics();
  if (!currentConsent) openConsent(false);

  document.addEventListener("click", function (event) {
    const consentButton = event.target.closest("[data-consent]");
    if (consentButton) {
      const action = consentButton.dataset.consent;
      if (action === "accept") writeConsent(true);
      if (action === "reject") writeConsent(false);
      if (action === "customize") setCustomize(true);
      if (action === "save") writeConsent(Boolean(analyticsToggle && analyticsToggle.checked));
      return;
    }

    const openPreferences = event.target.closest("[data-open-consent]");
    if (openPreferences) {
      openConsent(true);
      return;
    }

    const trackable = event.target.closest("[data-track]");
    if (trackable) {
      window.ammTrack(trackable.dataset.track, {
        location: trackable.dataset.trackLocation || "unknown"
      });
    }
  });

  const galleryDialog = document.getElementById("galleryDialog");
  const galleryImage = document.getElementById("galleryDialogImage");
  const galleryCaption = document.getElementById("galleryDialogCaption");
  let galleryReturnFocus = null;

  document.addEventListener("click", function (event) {
    const trigger = event.target.closest(".gallery-trigger");
    if (trigger && galleryDialog && typeof galleryDialog.showModal === "function") {
      galleryReturnFocus = trigger;
      galleryImage.src = trigger.dataset.full;
      galleryImage.alt = trigger.dataset.alt;
      galleryCaption.textContent = trigger.dataset.alt;
      galleryDialog.showModal();
      return;
    }

    if (event.target.closest("[data-close-gallery]") && galleryDialog) galleryDialog.close();
  });

  if (galleryDialog) {
    galleryDialog.addEventListener("click", function (event) {
      if (event.target === galleryDialog) galleryDialog.close();
    });
    galleryDialog.addEventListener("close", function () {
      galleryImage.src = "";
      if (galleryReturnFocus) galleryReturnFocus.focus();
    });
  }

  const briefingForm = document.getElementById("briefingForm");
  if (briefingForm) {
    let briefingStarted = false;
    briefingForm.addEventListener("input", function () {
      if (!briefingStarted) {
        briefingStarted = true;
        window.ammTrack("briefing_start", { location: "furniture-page" });
      }
    });

    briefingForm.addEventListener("submit", function (event) {
      event.preventDefault();
      if (!briefingForm.reportValidity()) return;

      const data = new FormData(briefingForm);
      const message = [
        "Olá, Mauricio! Vim pelo site da A Marcenaria Mágica.",
        "",
        "Meu nome: " + data.get("name"),
        "Região/bairro: " + data.get("region"),
        "Ambiente ou móvel: " + data.get("project"),
        "Prazo desejado: " + data.get("timeline"),
        "O que preciso: " + data.get("description")
      ].join("\n");

      window.ammTrack("briefing_submit", { location: "furniture-page" });
      const phone = briefingForm.dataset.whatsapp;
      window.open("https://wa.me/" + phone + "?text=" + encodeURIComponent(message), "_blank", "noopener");
    });
  }

  const navbarCollapse = document.getElementById("mainNavigation");
  if (navbarCollapse) {
    navbarCollapse.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        if (window.innerWidth < 992 && navbarCollapse.classList.contains("show") && window.bootstrap) {
          window.bootstrap.Collapse.getOrCreateInstance(navbarCollapse).hide();
        }
      });
    });
  }
})();
