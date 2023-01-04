module.exports = {
  eleventyComputed: {
    eleventyNavigation: {
      key: data => data.title,
      parent: data => data.title.charAt(0)
    }
  },
  layout: "tune",
  tags: [
      "tunes"
  ]
};