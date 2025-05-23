<template>
  <button
    ref="el"
    :class="{ VButton: true, [variant]: true, [size]: true }"
    @click="handleClick"
    @mouseenter="() => handleHover(true)"
    @mouseleave="() => handleHover(false)"
  >
    <div
      ref="bg"
      class="bg"
      :class="[backgroundColor ? `background-${backgroundColor}` : '']"
    />
    <div class="content">
      <IconBase v-if="iconLeft || size === 'icon'" :variant="icon" />
      <VText
        v-if="size === 'default'"
        :text="text"
        :variant="textVariant || 'medium-18'"
      />
      <IconBase v-if="iconRight" :variant="icon" />
    </div>
  </button>
</template>

<script setup>
import IconBase from "./IconBase.vue";
import VText from "./VText.vue";

import { defineProps, shallowRef } from "vue";

const el = shallowRef(null);
const bg = shallowRef(null);

const props = defineProps({
  text: {
    type: String,
    required: true,
  },
  variant: {
    type: String,
    // 'primary' | 'outline' | 'clear'
    default: "primary",
  },
  textVariant: {
    type: String,
  },
  size: {
    type: String,
    // 'default' | 'icon'
    default: "default",
  },
  onClick: {
    type: Function,
    default: () => {},
  },
  onHover: {
    type: Function,
    default: () => {},
  },
  iconLeft: {
    type: Boolean,
    default: false,
  },
  iconRight: {
    type: Boolean,
    default: false,
  },
  icon: {
    type: String,
    default: "gemini",
  },
  backgroundColor: {
    type: String,
    default: "primary",
  },
});

const handleClick = (e) => {
  e.preventDefault();
  // Add any additional click handling logic here
  props.onClick();
};

const handleHover = (isHovering) => {
  // Add any additional hover handling logic here
  props.onHover(isHovering);
};
</script>

<style lang="scss" scoped>
.VButton {
  position: relative;
  appearance: none;
  border: none;
  background: none;
  font: inherit;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 999px;
  cursor: pointer;
  box-shadow: 0px 14px 59.7px 0px rgba(0, 0, 0, 0.15);

  &.default {
    height: px-to-vh(54);
    padding: 0 px-to-vh(24);
  }

  &.icon {
    height: px-to-vh(54);
    width: px-to-vh(54);
    padding: 0;
  }

  .content {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}

.content {
  z-index: 3;
}

.bg {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Button */
.shopping,
.kayak,
.drive {
  .VButton.outline {
    .bg::after {
      display: none;
      content: "";
      position: absolute;
      width: calc(100% - 4px);
      aspect-ratio: 1;
      border-radius: 50%;
      padding: 3px;
      z-index: 2;
      transform: scale(0);
      transition: transform 0.3s ease-in-out;
    }
  }

  .VButton.primary,
  .VButton.clear {
    .bg::after {
      //display: none; //TODO: temporary as scale animation causes issues
      content: "";
      position: absolute;
      width: 100%;
      aspect-ratio: 1;
      border-radius: 50%;
      transform: scale(0);
      z-index: 0;
    }
  }
}

.shopping {
  .VButton.outline {
    color: #fff;
    transition: color 0.01s ease-in;

    .bg::before {
      background: linear-gradient(
        70.04deg,
        rgba(255, 255, 255, 0.5) -100.01%,
        rgba(66, 133, 244, 0.5) 182.1%
      );
      z-index: 1;
    }

    .bg::after {
      background: linear-gradient(
        70.04deg,
        #ffffff -100.01%,
        $brandBlue 182.1%
      );
    }

    &:hover {
      .bg::after {
        transform: scale(1);
        transition: transform 0.3s ease-in-out;
      }

      color: #333333;
      transition: color 0.01s ease-out;
    }
  }

  .VButton.clear {
    color: $grey;

    .bg {
      background: $darkBlue;

      @include gradient-border((45deg, #639bf5, #4285f4), 1px);
      position: absolute;

      &::before {
        border-radius: 999px;
        z-index: 1;
      }

      &::after {
        background: #3a445c;
        transition: transform 0.3s ease-in-out;
      }
    }

    &:hover {
      .bg::after {
        transform: scale(1);
      }
    }
  }

  .VButton.primary {
    color: #333333;

    .bg {
      background: linear-gradient(
        70.04deg,
        #ffffff -100.01%,
        $brandBlue 182.1%
      );

      &::after {
        background: $brandBlue;
        transition: transform 0.3s ease-in-out;
      }
    }

    &:hover {
      .bg::after {
        transform: scale(1);
      }
    }
  }
}

.kayak {
  .VButton.outline {
    color: #fff;
    transition: color 0.01s ease-in;

    .bg::before {
      background: linear-gradient(
        84.76deg,
        rgba(230, 244, 234, 0.5) -28.87%,
        rgba(52, 168, 83, 0.5) 163.54%
      );
    }

    .bg::after {
      background: linear-gradient(
        77.26deg,
        #e6f4ea -40.68%,
        $brandGreen 106.27%
      );
    }

    &:hover {
      .bg::after {
        transform: scale(1);
        transition: transform 0.3s ease-in-out;
      }

      color: #333333;
      transition: color 0.01s ease-out;
    }
  }

  .VButton.primary {
    color: #333333;

    .bg {
      background: linear-gradient(
        77.26deg,
        #e6f4ea -40.68%,
        $brandGreen 106.27%
      );

      &::after {
        background: $brandGreen;
        transition: transform 0.3s ease-in-out;
      }
    }

    &:hover {
      .bg::after {
        transform: scale(1);
      }
    }
  }
}

.drive {
  .VButton.outline {
    color: #fff;
    transition: color 0.01s ease-in;

    .bg::before {
      border: 1.5px solid;
      background: linear-gradient(
        87.08deg,
        rgba(255, 255, 255, 0.6) -9.68%,
        rgba(243, 178, 1, 0.6) 17.02%,
        rgba(227, 123, 36, 0.2) 101.2%
      );
    }

    .bg::after {
      background: linear-gradient(270deg, #e37b24 27.65%, #f3b201 118.57%);
    }

    &:hover {
      .bg::after {
        transform: scale(1);
        transition: transform 0.3s ease-in-out;
      }

      color: #333333;
      transition: color 0.01s ease-out;
    }
  }

  .VButton.primary {
    color: #333333;

    .bg {
      background: linear-gradient(270deg, #e37b24 27.65%, #f3b201 118.57%);

      &::after {
        background: $brandYellow;
        transition: transform 0.3s ease-in-out;
      }
    }

    &:hover {
      .bg::after {
        transform: scale(1);
      }
    }
  }
}

.skeeball {
  .VButton.primary {
    color: #fff;
    box-shadow:
      0px 0px 0px 1px rgba(0, 0, 0, 1),
      2px 4px 0px 0px rgba(0, 0, 0, 1);

    .bg {
      background: $brandGreen;
      &.background-yellow {
        background: $brandYellow;
      }
    }

    &:hover {
      box-shadow: 0px 0px 0px 1px rgba(0, 0, 0, 1);
      transform: translateX(1px) translateY(3px);
    }
  }
}
</style>
