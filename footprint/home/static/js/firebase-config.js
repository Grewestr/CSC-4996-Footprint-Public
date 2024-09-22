// Firebase configuration object
const firebaseConfig = {
  apiKey: "AIzaSyBrnuE0rPIse9NIoJiV0kw2FMEGDXShjBQ",
  authDomain: "footprint-2024.firebaseapp.com",
  databaseURL: "https://footprint-2024-default-rtdb.firebaseio.com",
  projectId: "footprint-2024",
  storageBucket: "footprint-2024.appspot.com",
  messagingSenderId: "998466139135",
  appId: "1:998466139135:web:017ddec8e02c17b4202dca",
  measurementId: "G-JF6P6GTTE3"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Initialize Firebase Authentication
const auth = firebase.auth(); // Use the Firebase Auth object
