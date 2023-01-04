module.exports = {
  eleventyComputed: {
    parent: data => data.title.charAt(0)
    
  },
  layout: "tune",
  tags: [
      "tunes"
  ]
};