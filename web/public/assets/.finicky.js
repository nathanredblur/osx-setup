module.exports = {
  defaultBrowser: 'Safari',
  handlers: [
    {
      // Open Gmail in Chrome
      match: /^https:\/\/mail\.google\.com/,
      browser: 'Google Chrome',
    },
    {
      // Open GitHub in preferred browser
      match: /github\.com/,
      browser: 'Google Chrome',
    },
    {
      // Open work domains in specific browser
      match: /company\.com/,
      browser: 'Microsoft Edge',
    },
  ],
};
