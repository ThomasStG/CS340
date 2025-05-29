import { Component, EventEmitter, Output } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';

import { ElectricalSearchService } from '../services/electrical-search.service';
import { UtilityService } from '../services/utility.service';

@Component({
  selector: 'app-electrical-item-search',
  templateUrl: './electrical-item-search.component.html',
  styleUrl: './electrical-item-search.component.css',
})
export class ElectricalItemSearchComponent {
  @Output() formSubmit = new EventEmitter<any>();
  @Output() clear = new EventEmitter<any>();
  electricalSearchForm = new FormGroup({
    type: new FormControl('', Validators.required),
    passiveType: new FormControl(''),
    passiveValue: new FormControl(0),
    passiveUnit: new FormControl({
      value: { value: 1, label: '' },
      disabled: false,
    }),
    passiveTolerance: new FormControl(0),
    mounting_method: new FormControl(''),
    search_percent: new FormControl(0.5),
    activeName: new FormControl(''),
    activeId: new FormControl(''),
    assemblyName: new FormControl(''),
    assemblyId: new FormControl(''),
    assemblyType: new FormControl(''),
  });
  errorMessage = '';
  multipliers: string[] = [];
  multiplier_values: number[] = [];

  constructor(
    private electricalSearchService: ElectricalSearchService,
    private utilityService: UtilityService,
  ) {}

  ngOnInit() {}
  onPassiveTypeChange() {
    const type = this.electricalSearchForm.get('passiveType')?.value;
    this.utilityService
      .getElectricalMultiplier()
      .subscribe(
        (data: { type: string; multiplier: string[]; values: number[] }[]) => {
          console.log(data);
          const found = data.find((item) => item.type === type);
          if (found) {
            this.multipliers = found.multiplier;
            this.multiplier_values = found.values;
            this.electricalSearchForm.get('passiveUnit')?.setValue({
              value: this.multiplier_values[0],
              label: this.multipliers[0],
            });
            console.log(this.multipliers);
            console.log(this.electricalSearchForm);
          } else {
            this.multipliers = [];
            this.multiplier_values = [];
            console.warn(`No multiplier data found for type: ${type}`);
          }
        },
      );
  }
  compareUnits(
    option: { value: number; label: string },
    value: { value: number; label: string },
  ): boolean {
    return option && value ? option.value === value.value : option === value;
  }

  onSubmit(action: string) {
    if (!this.electricalSearchForm.valid) {
    }
    var data = this.electricalSearchForm.value;
    if (data.type === 'passive' && data.passiveType === '') {
      this.errorMessage = 'Please select a passive type';
      return;
    }
    const unit = data.passiveUnit?.label;
    console.log(this.electricalSearchForm.value);
    const multiplier: number = Number(data.passiveUnit?.value);
    const value: number = Number(data.passiveValue);
    data.passiveValue = value * multiplier;
    console.log(data);
    switch (action) {
      case 'single':
        this.singleSearch(data, multiplier, unit);
        break;
      case 'multi':
        this.multiSearch(data, multiplier, unit);
        break;
    }
  }
  singleSearch(data: any, multiplier: number, unit?: string) {
    switch (data.type) {
      case 'active':
        this.errorMessage = '';
        if (data.activeName === '' && data.activeId === '') {
          this.errorMessage = 'Please enter either a name or an ID';
          return;
        }
        this.electricalSearchService
          .searchIdenticalActive(data.activeName, data.activeId)
          .subscribe((response) => {
            this.formSubmit.emit({
              items: response.data,
              type: 'active',
            });
          });
        break;
      case 'passive':
        this.electricalSearchService
          .searchIdenticalPassive(data.passiveType, data.passiveValue)
          .subscribe((response) => {
            this.formSubmit.emit({
              items: response.data,
              type: 'passive',
              subtype: data.passiveType,
              unit: unit,
              multiplier: multiplier,
            });
          });
        break;
      case 'assembly':
        this.electricalSearchService
          .searchIdenticalAssembly(
            data.assemblyType,
            data.assemblyName,
            data.assemblyId,
          )
          .subscribe((response) => {
            this.formSubmit.emit({
              items: response.data,
              type: 'assembly',
              subtype: data.assemblyType,
            });
          });
        break;
    }
  }
  multiSearch(data: any, multiplier: number, unit?: string) {
    switch (data.type) {
      case 'active':
        console.log(data.activeName);
        console.log(data.activeId);
        this.electricalSearchService
          .searchSimilarActive(data.activeName, data.activeId)
          .subscribe((response) => {
            this.formSubmit.emit({
              items: response.items,
              type: 'active',
            });
          });
        break;
      case 'passive':
        this.electricalSearchService
          .searchSimilarPassive(
            data.passiveValue,
            data.passiveTolerance,
            data.mounting_method,
            data.passiveType,
            data.search_percent,
          )
          .subscribe((response) => {
            this.formSubmit.emit({
              items: response.data.items,
              index: response.data.index,
              length: response.data.length,
              type: 'passive',
              subtype: data.passiveType,
              unit: unit,
              multiplier: multiplier,
            });
          });
        break;
      case 'assembly':
        this.electricalSearchService
          .searchSimilarAssembly(
            data.assemblyType,
            data.assemblyName,
            data.assemblyId,
          )
          .subscribe((response) => {
            this.formSubmit.emit({
              items: response.data,
              type: 'assembly',
              subtype: data.assemblyType,
            });
          });
        break;
    }
  }
  clearForm() {
    this.electricalSearchForm.reset();
    this.errorMessage = '';
    this.multipliers = [];
    this.multiplier_values = [];
    this.clear.emit();
  }
}
