const body = document.querySelector("body"),
  sidebar = body.querySelector("nav"),
  toggle = body.querySelector(".toggle"),
  searchBtn = body.querySelector(".search-box"),
  modeSwitch = body.querySelector(".toggle-switch"),
  modeText = body.querySelector(".mode-text");

toggle.addEventListener("click", () => {
  sidebar.classList.toggle("close");
});

searchBtn.addEventListener("click", () => {
  sidebar.classList.remove("close");
});

modeSwitch.addEventListener("click", () => {
  body.classList.toggle("dark");

  if (body.classList.contains("dark")) {
    modeText.innerText = "Light mode";
  } else {
    modeText.innerText = "Dark mode";
  }
});

function form_create() {
  var CONTINUE = confirm(
    "DOING THIS WILL DELETE YOUR PREVIOUS QUERY.Do you want to continue?"
  );
  if (CONTINUE === true) {
    var elem = document.getElementById("add_elem");
    elem.innerHTML = `<div class="container pd-20">
        <form action="/success" method="POST">
        <div class="form-group">
            <label class="col-md-5">Choose a bank of your choice : </label
            ><select name="bank" class="selectpicker">
            <option value='iob'>iob</option>
            <option value='sbi'>sbi</option>
          </select>
          </div>
          <div class="form-group">
            <label class="col-md-5">Select the category of the query</label
            ><select name="feature" class="selectpicker">
            <option value='loan'>loan</option>
          </select>
          </div>
          <div class="form-group"><label class="col-md-5">Enter your query : </label>
        <input name="query" class=\"form-control col-md-5\"type="textarea" name="query" id="query" required>
        </div>
        <input class="btn btn-success" type="submit" value="submit" />
        </form>
      </div>
        `;
  }
}
function togglePopup() {
  const element = document.getElementById("togglePopup");
  const button = document.getElementById("button1");
  if (element.style.display === "none") {
    button.style.innerHTML = "Show response chart";
    element.style.display = "block";
  } else {
    element.style.display = "none";
    button.style.innerHTML = "Hide response chart";
  }
}
var spanButton = document.getElementById("hideDisplaySpan");
spanButton.addEventListener("click", () => {
  const element = document.getElementById("togglePopup");
  const button = document.getElementById("button1");
  if (element.style.display == "none") {
    button.style.innerHTML = "Show response chart";
    element.style.display = "block";
  } else {
    element.style.display = "none";
    button.style.innerHTML = "Hide response chart";
  }
});
