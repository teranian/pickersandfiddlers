module.exports = {
  eleventyComputed: {
    eleventyNavigation: {
      key: data => data.title,
      parent: data => data.title.startsWith[0]
    }
  },
  layout: "tune",
  tags: [
      "tunes"
  ]
};