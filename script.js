// ---- REGISTER USER ----
function registerUser() {
  let name = document.getElementById("name").value;
  let age = document.getElementById("age").value;
  let voterId = document.getElementById("voterId").value;
  let password = document.getElementById("password").value;

  if (age < 18) {
    alert("You must be 18 or above to vote.");
    return false;
  }

  let voters = JSON.parse(localStorage.getItem("voters")) || [];

  // Check if Voter ID already exists
  if (voters.some(v => v.voterId === voterId)) {
    alert("Voter ID already registered.");
    return false;
  }

  voters.push({ name, age, voterId, password, hasVoted: false });
  localStorage.setItem("voters", JSON.stringify(voters));

  alert("Registration Successful! Please Login.");
  window.location.href = "index.html";
  return false;
}


// ---- LOGIN USER ----/
function loginUser() {
  let voterId = document.getElementById("voterId").value;

  let voters = JSON.parse(localStorage.getItem("voters")) || [];
  let voter = voters.find(v => v.voterId === voterId);

  if (!voter) {
    alert("Voter not registered.");
    return false;
  }

  localStorage.setItem("loggedInVoter", voterId);
  window.location.href = "vote.html";
  return false;
}


// ---- SUBMIT VOTE ----
function submitVote() {
  let selected = document.querySelector('input[name="candidate"]:checked');
  if (!selected) {
    alert("Please select a candidate.");
    return false;
  }

  let candidate = selected.value;
  let voters = JSON.parse(localStorage.getItem("voters")) || [];
  let voterId = localStorage.getItem("loggedInVoter");

  let voter = voters.find(v => v.voterId === voterId);

  if (voter.hasVoted) {
    alert("You have already voted!");
    window.location.href = "result.html";
    return false;
  }

  // Update vote count
  let votes = JSON.parse(localStorage.getItem("votes")) || {};
  votes[candidate] = (votes[candidate] || 0) + 1;

  // Mark voter as voted
  voter.hasVoted = true;

  localStorage.setItem("votes", JSON.stringify(votes));
  localStorage.setItem("voters", JSON.stringify(voters));

  alert("Vote submitted successfully!");
  window.location.href = "result.html";
  return false;
}


// ---- DISPLAY RESULTS ----
function displayResults() {
  let votes = JSON.parse(localStorage.getItem("votes")) || {};
  let resultDiv = document.getElementById("results");

  let output = "<ul>";
  output += `<li>Candidate A: ${votes["Candidate A"] || 0} votes</li>`;
  output += `<li>Candidate B: ${votes["Candidate B"] || 0} votes</li>`;
  output += `<li>Candidate C: ${votes["Candidate C"] || 0} votes</li>`;
  output += "</ul>";

  resultDiv.innerHTML = output;
}
