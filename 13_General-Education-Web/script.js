// document.addEventListener("DOMContentLoaded", function() {
//   var audio = document.getElementById("background-music");
//   audio.volume = 0.2; 
//   audio.currentTime = 0; // เริ่มเล่นที่วินาทีที่ 9
// });

document.addEventListener("DOMContentLoaded", function () {
  const audio = document.getElementById("background-music");
  audio.volume = 0.2;
  audio.currentTime = 0;
  const musicFolder = "music/"; 
  const songs = [
    // "DUET - OMORI .mp3",  
    "OMORI OST - 001 .mp3",
  //   "open-arms .mp3",
  //   "chill.mp3",
  //   "LANDOKMAI  เพลงรักเพลงแรก.mp3",
  //   "punyarb.mp3",
   ];

  function playRandomSong() {
    const randomIndex = Math.floor(Math.random() * songs.length); 
    const randomSong = songs[randomIndex]; 
    audio.src = musicFolder + randomSong; 
    audio.play(); 
  }

  // เล่นเพลงสุ่มเมื่อเพลงจบ
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
    //document.body.style.overflow = "hidden"; // ปิดการเลื่อนของ body เมื่อเปิด section
  }

  document.getElementById("resume-btn").addEventListener("click", function () {
    activateSection("resume-section");
  });

  document.getElementById("projects-btn").addEventListener("click", function () {
    activateSection("projects-section");
  });

  document.getElementById("contact-btn").addEventListener("click", function () {
    activateSection("contact-section");
    //document.body.style.overflow = "auto"; // เปิดการเลื่อนของ body เมื่อเปิด section contact
  });
});

