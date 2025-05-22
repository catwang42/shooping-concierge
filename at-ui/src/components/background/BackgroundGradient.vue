<template></template>

<script setup>
import { onBeforeUnmount, onMounted, toRaw, watchEffect, ref } from "vue";
import { Color, Mesh, Program, Triangle, Vec2 } from "ogl";
import { nextTick } from "vue";
import gradVertex from "./shaders/gradVert.glsl";
import gradFragment from "./shaders/gradFrag.glsl";
import { eventBus } from "@/utils/event-bus";
import { gsap } from "@/utils/gsap";
import { states } from "./states";
// Declare a prop for the oglState
const props = defineProps({
  oglState: {
    type: Object,
    required: true,
  },
  bgColor: {
    type: String,
    required: true,
  },
  disk1: {
    type: Object,
    required: true,
  },
  disk2: {
    type: Object,
    required: true,
  },
  disk3: {
    type: Object,
    required: true,
  },
  disk4: {
    type: Object,
    required: true,
  },
  fade: {
    type: Number,
    required: true,
  },
  animate: {
    type: Boolean,
    required: true,
    default: true,
  },
  useStates: {
    type: Boolean,
    required: false,
    default: true,
  },
});

let mesh = null;

const diskProps = ["disk1", "disk2", "disk3", "disk4"];

// Helper function to create disk uniforms
const createDiskUniforms = (gl, diskData) => ({
  color: { value: new Color(diskData.color) },
  center: { value: new Vec2(diskData.center.x, diskData.center.y) },
  radius: { value: diskData.radius },
});

const pauseIdle = ref(false);
const programRef = ref(null);
const lastState = ref(null);

const targetStateRef = ref({
  ...states["idle"],
});

onMounted(() => {
  const { oglState } = props;

  nextTick(() => {
    if (oglState) {
      setup(oglState);
    }
  });

  eventBus.on("animate-background", (state) => {
    updateUniforms(state);
  });
});

function updateUniforms(state) {
  const currentState = states[state];
  const uniforms = programRef.value.uniforms;

  const obj = {
    value: 0,
  };

  const parabolaCurve = (x, k) => {
    return Math.pow(4.0 * x * (1.0 - x), k);
  };

  gsap.to(obj, {
    value: 1,
    duration: 3,
    ease: "power1.inOut",
    onUpdate: () => {
      //uniforms.uFade.value = 1.0 - 0.5 * parabolaCurve(obj.value, 1);
    },
  });

  gsap.to(uniforms.uFade, {
    value: currentState.fade,
    duration: 3,
    ease: "power1.inOut",
  });

  Object.keys(currentState).forEach((key) => {
    if (key === "animate" || key === "bgColor") return;
    const uniformName = `u${key.charAt(0).toUpperCase()}${key.slice(1)}`;

    let index = 0;

    if (uniformName.includes("Disk")) {
      index = diskProps.indexOf(key);

      gsap.to(uniforms[uniformName].center.value, {
        x: currentState[key].center.x,
        y: currentState[key].center.y,
        duration: 4,
        delay: index * 1,
        ease: "power1.inOut",
      });

      gsap.to(uniforms[uniformName].radius, {
        value: currentState[key].radius,
        duration: 4,
        delay: index * 1,
        ease: "power1.inOut",
      });
    }
  });
}

window.updateUniforms = updateUniforms;

function setup(oglState) {
  const { gl, scene } = oglState;

  const geometry = new Triangle(gl);

  // Create uniforms object dynamically
  const uniforms = {
    uBGColor: { value: new Color(props.bgColor) },
    uResolution: { value: new Vec2(window.innerWidth, window.innerHeight) },
    uFade: { value: props.fade },
    uTime: { value: 0.0 },
  };

  // Add disk uniforms dynamically
  diskProps.forEach((diskProp) => {
    uniforms[`u${diskProp.charAt(0).toUpperCase()}${diskProp.slice(1)}`] =
      createDiskUniforms(gl, props[diskProp]);
  });

  const program = new Program(gl, {
    vertex: gradVertex,
    fragment: gradFragment,
    uniforms,
  });

  programRef.value = program;

  const data = props.useStates ? targetStateRef.value : props;

  program.uniforms.uBGColor.value = new Color(data.bgColor);
  program.uniforms.uFade.value = data.fade;
  // Update disk uniforms dynamically
  diskProps.forEach((diskProp) => {
    const uniformName = `u${diskProp.charAt(0).toUpperCase()}${diskProp.slice(1)}`;
    program.uniforms[uniformName].color.value.set(data[diskProp].color);
    program.uniforms[uniformName].center.value.set(
      data[diskProp].center.x,
      data[diskProp].center.y
    );
    program.uniforms[uniformName].radius.value = data[diskProp].radius;
  });

  mesh = new Mesh(gl, { geometry, program });
  mesh.setParent(scene);

  oglState.onRender = (t) => {
    if (!props.animate) return;
    if (pauseIdle.value) return;
    program.uniforms.uTime.value = t;
    //just an example of how to animate the disks
    program.uniforms.uDisk1.center.value.x += Math.sin(t * 0.2) * 0.002;
    program.uniforms.uDisk3.center.value.y += Math.cos(t * 0.2) * 0.001;
    program.uniforms.uDisk4.center.value.y += Math.cos(t * 0.2) * 0.001;
  };
  window.addEventListener("resize", () => {
    program.uniforms.uResolution.value.set(
      window.innerWidth,
      window.innerHeight
    );
  });
}

function setState(state) {
  Object.keys(state).forEach((key) => {
    //targetStateRef.value[key] = state[key]

    const fade = state.fade;

    gsap.to(targetStateRef.value, {
      fade,
      duration: 1,
      ease: "power1.inOut",
    });

    if (key.includes("disk")) {
      const target = state[key];

      const targetCenter = target.center;
      const targetRadius = target.radius;

      gsap.to(targetStateRef.value[key].center, {
        x: targetCenter.x,
        y: targetCenter.y,
        duration: 3,
        ease: "linear",
      });

      gsap.to(targetStateRef.value[key].radius, {
        value: targetRadius,
        duration: 3,
        ease: "linear",
      });
    }
  });
}

function animateIn() {
  console.log("animateIn");
}

function animateOut() {
  console.log("animateOut");
}

function animateSet() {
  console.log("animateSet");
}

defineExpose({
  setState,
  animateIn,
  animateOut,
  animateSet,
});

onBeforeUnmount(() => {
  const { oglState } = props;
  const scene = toRaw(oglState.scene);
  // Clean up the mesh when the child is unmounted (e.g., on HMR)
  scene.traverse((child) => {
    if (child === mesh) {
      child.setParent(null);
    }
  });
});
</script>
