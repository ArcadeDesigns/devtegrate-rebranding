function FaqOpener() {
	let answers=document.querySelectorAll('.accordion');
    answers.forEach((event)=>{
      event.addEventListener('click',()=>{
        if(event.classList.contains('active')){
          event.classList.remove('active');

        }
        else{
          event.classList.add('active');
        }
      })
    });
}

function DropDownMenuFocus() {
  const dropdowns = document.querySelectorAll('.drop-down > span');
  dropdowns.forEach(dropdown => {
    dropdown.addEventListener('click', function() {
      const parent = this.parentElement;

      // Close any open dropdowns except the one being clicked
      document.querySelectorAll('.drop-down.active').forEach(activeDropdown => {
        if (activeDropdown !== parent) {
          activeDropdown.classList.remove('active');
        }
      });

      // Toggle the clicked dropdown
      parent.classList.toggle('active');
    });
  });
};

function ShowContent() {
  const identifiers = document.querySelectorAll('.updated-swiper-identifier');
  const grids = document.querySelectorAll('.updated-swiper-ctn-grid');

  identifiers.forEach((identifier, index) => {
    identifier.addEventListener('click', function() {
    // Remove 'active' class from all identifiers and grids
      identifiers.forEach(id => id.classList.remove('active'));
      grids.forEach(grid => grid.classList.remove('active'));

      // Add 'active' class to the clicked identifier and the corresponding grid
      identifier.classList.add('active');
      grids[index].classList.add('active');
    });
  });
};
