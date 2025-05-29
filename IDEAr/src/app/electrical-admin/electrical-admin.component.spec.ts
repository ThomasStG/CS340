import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ElectricalAdminComponent } from './electrical-admin.component';

describe('ElectricalAdminComponent', () => {
  let component: ElectricalAdminComponent;
  let fixture: ComponentFixture<ElectricalAdminComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ElectricalAdminComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ElectricalAdminComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
