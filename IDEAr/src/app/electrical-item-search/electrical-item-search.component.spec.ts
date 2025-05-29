import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ElectricalItemSearchComponent } from './electrical-item-search.component';

describe('ElectricalItemSearchComponent', () => {
  let component: ElectricalItemSearchComponent;
  let fixture: ComponentFixture<ElectricalItemSearchComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ElectricalItemSearchComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ElectricalItemSearchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
