const yaml = require("js-yaml");
const { DateTime } = require("luxon");
const syntaxHighlight = require("@11ty/eleventy-plugin-syntaxhighlight");
const htmlmin = require("html-minifier");
const embedYouTube = require("eleventy-plugin-youtube-embed");
const eleventyNavigationPlugin = require("@11ty/eleventy-navigation");
const _ = require("lodash");

module.exports = function (eleventyConfig) {
  // Disable automatic use of your .gitignore
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
    "./src/static/css/": "./static/css/"});


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


  // Let Eleventy transform HTML files as nunjucks
  // So that we can use .html instead of .njk
  return {
    dir: {
      input: "src",
    },
    htmlTemplateEngine: "njk",
  };
};

