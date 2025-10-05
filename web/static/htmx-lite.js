(function () {
  function serializeForm(form, encoding) {
    if (encoding === 'multipart/form-data') {
      return new FormData(form);
    }
    const params = new URLSearchParams();
    new FormData(form).forEach((value, key) => {
      params.append(key, value instanceof File ? value.name : value);
    });
    return params;
  }

  function handleSubmit(event) {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) {
      return;
    }
    const postUrl = form.getAttribute('hx-post');
    const getUrl = form.getAttribute('hx-get');
    if (!postUrl && !getUrl) {
      return;
    }
    event.preventDefault();
    const method = postUrl ? 'POST' : 'GET';
    const url = postUrl || getUrl || form.action;
    const targetSelector = form.getAttribute('hx-target');
    const swap = form.getAttribute('hx-swap') || 'innerHTML';
    const encoding = form.getAttribute('hx-encoding') || form.enctype;
    const body = method === 'GET' ? undefined : serializeForm(form, encoding);

    const requestInit = { method, headers: {} };
    if (body !== undefined) {
      requestInit.body = body;
    }

    fetch(url, requestInit)
      .then((response) => {
        if (!response.ok) {
          throw new Error('Request failed with status ' + response.status);
        }
        const contentType = response.headers.get('Content-Type') || '';
        if (contentType.includes('application/json')) {
          return response.json().then((data) => JSON.stringify(data, null, 2));
        }
        return response.text();
      })
      .then((payload) => {
        if (!targetSelector) {
          return;
        }
        const target = document.querySelector(targetSelector);
        if (!target) {
          return;
        }
        if (swap === 'outerHTML') {
          target.outerHTML = payload;
        } else if (swap === 'textContent') {
          target.textContent = payload;
        } else {
          target.innerHTML = payload;
        }
      })
      .catch((error) => {
        if (!targetSelector) {
          return;
        }
        const target = document.querySelector(targetSelector);
        if (target) {
          target.textContent = 'Error: ' + error.message;
        }
      });
  }

  document.addEventListener('submit', handleSubmit, true);
})();
