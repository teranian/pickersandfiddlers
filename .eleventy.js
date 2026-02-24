const yaml = require("js-yaml");
const { DateTime } = require("luxon");
const syntaxHighlight = require("@11ty/eleventy-plugin-syntaxhighlight");
const htmlmin = require("html-minifier");
const embedYouTube = require("eleventy-plugin-youtube-embed");
const eleventyNavigationPlugin = require("@11ty/eleventy-navigation");
const _ = require("lodash");

module.exports = function (eleventyConfig) {
  // Disable automatic use of your .gitignore
  eleventyConfig.setServerOptions({
		// Default values are shown:

		// Whether the live reload snippet is used
		liveReload: true,

		// Whether DOM diffing updates are applied where possible instead of page reloads
		domDiff: true,

		// The starting port number
		// Will increment up to (configurable) 10 times if a port is already in use.
		port: 8080,

		// Additional files to watch that will trigger server updates
		// Accepts an Array of file paths or globs (passed to `chokidar.watch`).
		// Works great with a separate bundler writing files to your output folder.
		// e.g. `watch: ["_site/**/*.css"]`
		watch: [],

		// Show local network IP addresses for device testing
		showAllHosts: false,

		// Use a local key/certificate to opt-in to local HTTP/2 with https
		https: {
			// key: "./localhost.key",
			// cert: "./localhost.cert",
		},

		// Change the default file encoding for reading/serving files
		encoding: "utf-8",

		// Show the dev server version number on the command line
		showVersion: false,

		// Added in Dev Server 2.0+
		// The default file name to show when a directory is requested.
		indexFileName: "index.html",

		// Added in Dev Server 2.0+
		// An object mapping a URLPattern pathname to a callback function
		// for on-request processing (read more below).
		onRequest: {},
	});

  eleventyConfig.amendLibrary("md", mdLib => mdLib.enable("code"));

  eleventyConfig.setUseGitIgnore(false);

  // Merge data instead of overriding
  eleventyConfig.setDataDeepMerge(true);

  // human readable date
  eleventyConfig.addFilter("readableDate", (dateObj) => {
    return DateTime.fromJSDate(dateObj, { zone: "utc" }).toFormat(
      "dd LLL yyyy"
    );
  });

  // Syntax Highlighting for Code blocks
  eleventyConfig.addPlugin(syntaxHighlight);

  eleventyConfig.addPlugin(eleventyNavigationPlugin);

  // A plugin to automatically convert any youtube link found in markdown files into an embed iframe
  eleventyConfig.addPlugin(embedYouTube, {
    embedClass: 'my-alternate-classname',
    modestBranding: true,
    noCookie: true
  });

  // To Support .yaml Extension in _data
  // You may remove this if you can use JSON
  eleventyConfig.addDataExtension("yaml", (contents) => yaml.load(contents));

  // Copy Static Files to /_Site
  eleventyConfig.addPassthroughCopy({
    "./src/admin/config.yml": "./admin/config.yml",
    "./node_modules/alpinejs/dist/cdn.min.js": "./static/js/alpine.js",
    "./node_modules/prismjs/themes/prism-tomorrow.css": "./static/css/prism-tomorrow.css",
    "./node_modules/abcjs/dist/abcjs-basic.js": "./static/js/abcjs-basic.js",
    "./node_modules/abcjs/dist/abcjs-basic.js.map": "./static/js/abcjs-basic.js.map",
    "./node_modules/abcjs/dist/abcjs-plugin-min.js": "./static/js/abcjs-plugin-min.js",
    "./src/static/js/abcscripts.js": "./static/js/abcscripts.js",
  });

  // Copy Image Folder to /_site
  eleventyConfig.addPassthroughCopy({
    "./src/static/css/": "./static/css/"
  });

  // Copy Image Folder to /_site
  eleventyConfig.addPassthroughCopy("./src/static/img");

  // Copy favicon to route of /_site
  eleventyConfig.addPassthroughCopy("./src/favicon.ico");

  // Minify HTML
  // eleventyConfig.addTransform("htmlmin", function (content, outputPath) {
  //   // Eleventy 1.0+: use this.inputPath and this.outputPath instead
  //   if (outputPath.endsWith(".html")) {
  //     let minified = htmlmin.minify(content, {
  //       useShortDoctype: true,
  //       removeComments: true,
  //       collapseWhitespace: true,
  //     });
  //     return minified;
  //   }

  //   return content;
  // });

  // this sorts a Collection descending by Title A > Z
  eleventyConfig.addFilter('sortByTitle', values => {
    return values.slice().sort((a, b) => a.data.title.localeCompare(b.data.title))
  });

  eleventyConfig.addCollection("alphabetGroups", function(collectionApi) {
    // get unsorted items.
    let array = collectionApi.getAll();
    array =  array.map(a => a.data.parent);
    return [...new Set(array.sort())];
  });

  eleventyConfig.addCollection("tunesByKey", function(collectionApi) {
    // get unsorted items.
    let array = collectionApi.getAllSorted();
    array =  array.map(a => a.data.key)
    return [...new Set(array.sort())];
  });



  return {
    dir: {
      input: "src",
    },
    htmlTemplateEngine: "njk",
  };
};