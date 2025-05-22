import { defineStore } from 'pinia'

export const useProductsStore = defineStore('products', {
  state: () => ({
    products: [],
    count: 0,
    currentProductName: "",
    currentProductGroupID: null,
    currentProductIconID: null,
    selectedProductID: null,
    modalOpen: false,
    cartOpen: false,
    cartProducts: [],
  }),
  actions: {
    setSockets(sockets) {
      this.sockets = sockets;
        this.sockets.on('present-items', ({items}) => {
          console.log("present-items: received: " + this.currentProductGroupID + ", items: " + items.length)
          items.forEach(item => {
            this.addProduct({
              id: item.id,
              index: this.count,
              groupID: this.currentProductGroupID,
              imageID: item.id,
              name: item.name,
              description: item.description,
          })
        })
      })
      this.sockets.on('set-product-group', ({group_id, item_category, group_icon_id, queries}) => {
//        this.setProductGroup({productName: queries[0], group_id, group_icon_id});
        this.setProductGroup({productName: item_category, group_id, group_icon_id});
      })
      this.sockets.on('clear-products', () => {
        this.clearProducts();
      })
    },
    addProduct(product) {
      this.products.push(product)
      this.count++
    },
    setCartOpen(open, productID) {
      if(productID) {
        const product = this.products.find(product => product.id === productID)
        if(product) {
          this.cartProducts.push(product)
        }
      }
      this.cartOpen = open;
    },
    setModalOpen(open) {
      this.modalOpen = open;
    },
    setProductGroup({productName, group_id, group_icon_id}) {
      this.currentProductName = productName
      this.currentProductGroupID = group_id
      this.currentProductIconID = group_icon_id
    },
    setSelectedProduct(id) {
      this.selectedProductID = id
      if(id) {
        this.setModalOpen(true);
      }else{
        this.setModalOpen(false);
      }
    },
    clearProducts() {
      if(this.products.length > 0) {
        this.products = []
        this.currentProductName = null
        this.currentProductGroupID = 0
        this.count = 0
      }
    },
    mockProducts(count = 10) {
      for(let i = 0; i < count; i++) {
        this.addProduct({
          id: i,
          name: `Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.`,
          index: i,
          //price: 100,
          //store: "Store 1",
          description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        })
      }
    },
    getSelectedProduct() {
      return this.products.find(product => product.id === this.selectedProductID)
    },
    resetAll() {
      this.clearProducts();
      this.currentProductName = "";
      this.currentProductGroupID = null;
      this.currentProductIconID = null;
      this.selectedProductID = null;
    }
  },
})

/**
 * @typedef {Object} Product
 * @property {number} id - The ID of the product
 * @property {number} groupID - The ID of the group that the product belongs to
 * @property {string} name - The name of the product
 * @property {string} price - The price of the product
 * @property {string} store - The store that the product belongs to
 * @property {string} description - The description of the product
 */