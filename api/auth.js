export default function handler(req, res) {
  const { GITHUB_CLIENT_ID } = process.env;
  const scope = 'repo,user';
  const state = Math.random().toString(36).slice(2);
  res.setHeader('Set-Cookie', `oauth_state=${state}; HttpOnly; Secure; SameSite=Lax; Path=/`);
  res.redirect(
    `https://github.com/login/oauth/authorize?client_id=${GITHUB_CLIENT_ID}&scope=${scope}&state=${state}`
  );
}
