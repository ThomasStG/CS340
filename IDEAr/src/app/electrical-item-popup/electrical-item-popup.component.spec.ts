import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ElectricalItemPopupComponent } from './electrical-item-popup.component';

describe('ElectricalItemPopupComponent', () => {
  let component: ElectricalItemPopupComponent;
  let fixture: ComponentFixture<ElectricalItemPopupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ElectricalItemPopupComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ElectricalItemPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
