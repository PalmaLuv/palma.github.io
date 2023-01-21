window.onload = function () {
    document.body.classList.add('loaded_hiding');
    window.setTimeout(function () {
      document.body.classList.add('loaded');
      document.body.classList.remove('loaded_hiding');
    }, 500);
  }

  const frames = ['( o.o)', '( -.-)','( o.o)'];
  setInterval(
    () => {
      const frame = frames.shift();
      document.title = frame;
      frames.push(frame);
    },
    6000,
  );