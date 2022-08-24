window.onload = function () {

  new ABCJS.Editor('abc', {
    canvas_id: 'paper',
    generate_warnings: true,
    warnings_id: 'warnings',
    synth: {
      el: '#audio',
      options: {
        displayRestart: true,
        displayPlay: true,
        displayProgress: true,
        displayWarp: true
      },
      audioParams: {
        qpm: 80
      }
    },
    abcjsParams: {
      responsive: 'resize',
      oneSvgPerLine: false,
    },
  });

  // 	var cursorControl = {...}; // see section on CursorControl

  // 	{# var abc = "X:1\n etc..."; #}

  // 	var abcOptions = {
  // 		add_classes: true
  // 	};
  // 	var audioParams = {
  // 		chordsOff: true
  // 	};

  // 	if (ABCJS.synth.supportsAudio()) {
  // 		var synthControl = new ABCJS
  // 			.synth
  // 			.SynthController();
  // 		synthControl.load("#audio", cursorControl, {
  // 			displayLoop: true,
  // 			displayRestart: true,
  // 			displayPlay: true,
  // 			displayProgress: true,
  // 			displayWarp: true
  // 		});

  // 		var visualObj = ABCJS.renderAbc("paper", abc, abcOptions);
  // 		var createSynth = new ABCJS
  // 			.synth
  // 			.CreateSynth();
  // 		createSynth
  // 			.init({visualObj: visualObj[0]})
  // 			.then(function () {
  // 				synthControl
  // 					.setTune(visualObj[0], false, audioParams)
  // 					.then(function () {
  // 						console.log("Audio successfully loaded.")
  // 					})
  // 					.catch(function (error) {
  // 						console.warn("Audio problem:", error);
  // 					});
  // 			})
  // 			.catch(function (error) {
  // 				console.warn("Audio problem:", error);
  // 			});
  // 	} else {
  // 		document
  // 			.querySelector("#audio")
  // 			.innerHTML = "Audio is not supported in this browser.";
  // 	}
  // }
};
