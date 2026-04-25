export default async function handler(req, res) {
  const { code } = req.query;
  const { GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET } = process.env;

  const tokenRes = await fetch('https://github.com/login/oauth/access_token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({
      client_id: GITHUB_CLIENT_ID,
      client_secret: GITHUB_CLIENT_SECRET,
      code,
    }),
  });
  const { access_token } = await tokenRes.json();

  res.setHeader('Content-Type', 'text/html');
  res.send(`<!DOCTYPE html><html><body>
    <script>
      const token = ${JSON.stringify(access_token)};
      const msg = JSON.stringify({ token, provider: 'github' });
      function sendAndClose() {
        if (window.opener) {
          // Sveltia CMS popup flow
          window.opener.postMessage('authorization:github:success:' + msg, '*');
          setTimeout(() => window.close(), 500);
        } else {
          // Dashboard same-window flow — redirect back with token in hash
          window.location.href = '/admin/#gh_token=' + encodeURIComponent(token);
        }
      }
      sendAndClose();
    </script>
  </body></html>`);
}
