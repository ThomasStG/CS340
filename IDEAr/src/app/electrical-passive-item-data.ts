export interface ElectricalPassiveItemData {
  id: number;
  subtype: string;
  value: number;
  mounting_method: string;
  tolerance: number;
  part_number: string;
  location: string;
  rack: number;
  slot: string;
  count: number;
  link: string;
  is_contacted: boolean;
  max_power: number;
  max_voltage: number;
  max_current: number;
  current_hold: number;
  polarity: boolean;
  seller: string;
  dielectric_material: string;
}
