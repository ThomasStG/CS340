import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ElectricalAdminSearchComponent } from './electrical-admin-search.component';

describe('ElectricalAdminSearchComponent', () => {
  let component: ElectricalAdminSearchComponent;
  let fixture: ComponentFixture<ElectricalAdminSearchComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ElectricalAdminSearchComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ElectricalAdminSearchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
