export type Product = {
  uuid: string;
  sku: string;
  name: string;
  description: string | null;
  unitCode: string;
  measureQuantity: string;
  purchasePriceBob: string;
  salePriceBob: string;
  availableQuantity: string | null;
  availability: string;
};
