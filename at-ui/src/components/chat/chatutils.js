import gsap from "gsap";

const animateIn = (el) => {
  console.log(el);
  gsap.to(el, {
    x: 0,
    opacity: 1,
    ease: "back.out",
  });
};

const animateOut = (el) => {
  gsap.to(el, {
    x: 100,
    opacity: 0,
    ease: "back.in",
  });
};

const animateSet = (el) => {
  gsap.set(el, {
    x: 100,
    opacity: 0,
  });
};

export { animateIn, animateOut, animateSet };