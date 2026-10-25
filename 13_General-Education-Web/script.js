document.addEventListener("DOMContentLoaded", function () {
  const audio = document.getElementById("background-music");
  audio.volume = 0.2;
  audio.currentTime = 0;
  const musicFolder = "music/";
  const songs = [

    "OMORI OST - 001 .mp3",


   ];

  function playRandomSong() {
    const randomIndex = Math.floor(Math.random() * songs.length);
    const randomSong = songs[randomIndex];
    audio.src = musicFolder + randomSong;
    audio.play();
  }


  audio.addEventListener("ended", playRandomSong);


  playRandomSong();
});


    document.getElementById("contact-section").addEventListener("animationstart", function () {
      const elements = document.querySelectorAll("#contact-section .animate-text");
      elements.forEach((element, index) => {
        element.style.animationDelay = `${index * 0.5}s`;
      });
    });
     document.addEventListener("DOMContentLoaded", function () {
  function activateSection(sectionId) {
    document.querySelectorAll(".resume-section").forEach((section) => {
      section.classList.remove("active");
    });
    document.getElementById(sectionId).classList.add("active");

  }

  document.getElementById("resume-btn").addEventListener("click", function () {
    activateSection("resume-section");
  });

  document.getElementById("projects-btn").addEventListener("click", function () {
    activateSection("projects-section");
  });

  document.getElementById("contact-btn").addEventListener("click", function () {
    activateSection("contact-section");

  });
});
