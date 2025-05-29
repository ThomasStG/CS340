import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ElectricalAdminPopupComponent } from './electrical-admin-popup.component';

describe('ElectricalAdminPopupComponent', () => {
  let component: ElectricalAdminPopupComponent;
  let fixture: ComponentFixture<ElectricalAdminPopupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ElectricalAdminPopupComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ElectricalAdminPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
