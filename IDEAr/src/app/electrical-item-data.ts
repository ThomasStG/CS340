export interface ElectricalItemData {
  type: string;
  name: string;
  part_id: number;
  id: number;
  description: string;
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
  max_v: number;
  max_p: number;
  max_i: number;
  i_hold: number;
  polarity: boolean;
  seller: string;
  dielectric_material: string;
  is_assembly: boolean;
}
