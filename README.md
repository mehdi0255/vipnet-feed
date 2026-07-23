# VIPNet public feed

This repository builds the public feed used by VIPNet. It uses only the public web pages of the approved Telegram channels; it requires no Telegram account, API key, phone number, or user data.

## One-time GitHub setup

1. Create a **public** repository, for example `vipnet-feed`.
2. Upload the contents of this folder to the repository root.
3. In **Settings → Pages**, set **Build and deployment → Source** to **GitHub Actions**.
4. Open the **Actions** tab, choose **Update VIPNet public feed**, and select **Run workflow** once.
5. The feed URL will be:
   `https://YOUR-GITHUB-USERNAME.github.io/vipnet-feed/configs.json`

Paste that exact URL into the VIPNet app's feed setting. The workflow checks the public sources approximately every four hours; you can also run it manually from the Actions tab.

## Privacy and limitations

- No user data is collected or stored by this repository.
- The published feed is public because an APK cannot safely contain a GitHub access secret. Anyone with the feed URL can retrieve the published configurations.
- Source-provided display labels are removed from URI-style links. VMess `ps` labels are replaced with a generated `VIP-...` label.
- Telegram may change or throttle its public web pages. If that happens, the collector may need an update.
